import os
import time
import pyotp
from playwright.async_api import async_playwright, Page, BrowserContext
from engine.drivers.base_driver import BaseDriver
from engine.scripts.utils.paths import get_store_root

class AdminPanelDriver(BaseDriver):
    """
    Unified Driver for automating Admin Panels (Jeetup, Larkup, Kanzplay, etc.).
    Handles Login + Google 2FA + Session Persistence via GUI Simulation.
    """
    
    def _validate_config(self):
        """Required by BaseDriver."""
        # Check if URL is present (credentials might be loaded later or lazy)
        if not self.config.get("admin_panel", {}).get("url"):
            # We might allow it if user just wants to use driver for other things? 
            # But standard is to validate core requirements.
            pass

    def __init__(self, config=None):
        super().__init__(config) # BaseDriver stores self.config
        
        # Default to Kanz if not specified, but usually comes from config
        self.url = self.config.get("admin_panel", {}).get("url")
        self.headless = self.config.get("admin_panel", {}).get("headless", True)
        self.app_name = self.config.get('app_name', 'unknown')
        
        # Session Persistence Path
        store_root = get_store_root()
        self.session_path = store_root / "operations" / self.app_name / "session" / "auth.json"
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(self.session_path), exist_ok=True)
        
        # Load Credentials from Env
        self.username = os.environ.get("ADMIN_USERNAME") or os.environ.get(f"{self.app_name.upper()}_ADMIN_USERNAME")
        self.password = os.environ.get("ADMIN_PASSWORD") or os.environ.get(f"{self.app_name.upper()}_ADMIN_PASSWORD")
        self.totp_secret = os.environ.get("ADMIN_TOTP_SECRET") or os.environ.get(f"{self.app_name.upper()}_ADMIN_TOTP_SECRET")
        
        # For Kanzplay specific case mentioned by user
        if not self.username: self.username = os.environ.get("KANZ_ADMIN_USERNAME")
        if not self.password: self.password = os.environ.get("KANZ_ADMIN_PASSWORD")
        if not self.totp_secret: self.totp_secret = os.environ.get("KANZ_ADMIN_TOTP_SECRET")

    async def login(self, otp_code: str = None) -> Page:
        """
        Launches browser, performs login with 2FA (if needed), and returns the authenticated Page.
        Uses cached session if available and valid.
        """
        if not self.url:
            raise ValueError("Admin Panel URL not configured in config.yaml under 'admin_panel.url'")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=self.headless)
        
        # Try Loading State
        context = None
        if os.path.exists(self.session_path):
            try:
                context = await browser.new_context(storage_state=self.session_path)
                # Verify validity by navigating to dashboard
                page = await context.new_page()
                await page.goto(self.url) # Usually redirects to dashboard if logged in
                try:
                    await page.wait_for_url("**/dashboard", timeout=5000)
                    print(f"✅ Reused valid Admin Session: {self.session_path}")
                    return page
                except:
                    print("⚠️ Cached session expired or invalid. Re-logging in.")
                    await context.close()
                    context = None
            except Exception as e:
                print(f"Failed to load session: {e}")
        
        # Fresh Login
        if not context:
             context = await browser.new_context()

        page = await context.new_page()
        
        # Navigate
        await page.goto(self.url)
        await page.wait_for_load_state("networkidle")
        
        # If we are already logged in (redirected immediately), save and return
        if "/dashboard" in page.url:
             await context.storage_state(path=self.session_path)
             return page

        # Dispatch based on type
        panel_type = self.config.get("admin_panel", {}).get("type", "default").lower()
        
        if panel_type == "wg":
            await self._login_wg(page, otp_code)
        else:
            await self._login_default(page, otp_code)
        
        return page

    async def _login_default(self, page: Page, otp_code: str = None):
        """Standard login flow (A23/Kanz/etc)"""
        if not all([self.username, self.password]):
             raise ValueError("Missing Admin Username/Password in .env")
        
        await page.fill("input[placeholder='Username']", self.username)
        await page.fill("input[placeholder='Password']", self.password)
        
        final_otp = self._get_otp(otp_code)
        await page.fill("input[placeholder='Google OTP']", final_otp)
        
        try:
             await page.get_by_role("button", name="Login").click()
        except:
             await page.click("button.el-button--primary")
        
        await self._wait_for_dashboard(page)

    async def _login_wg(self, page: Page, otp_code: str = None):
        """WG Platform Login Flow (XP786)"""
        if not all([self.username, self.password]):
             raise ValueError("Missing Admin Username/Password in .env")

        try:
            await page.fill("input[type='text']", self.username)
        except:
            await page.fill("input[placeholder*='sername']", self.username)
            
        try:
            await page.fill("input[type='password']", self.password)
        except:
            await page.fill("input[placeholder*='assword']", self.password)

        # 2. Click Login
        try:
            login_btn = page.locator("button:has-text('登录'), button:has-text('Login')")
            if await login_btn.count() > 0:
                await login_btn.last.click() 
            else:
                await page.click("button[type='button'].el-button--primary")
        except Exception as e:
            print(f"[Warn] Click login failed: {e}")

        # 3. Handle Potential OTP Modal
        try:
            await page.wait_for_timeout(2000)
            modal_input = page.locator(".el-message-box__input input")
            
            if await modal_input.count() > 0 and await modal_input.is_visible():
                print("   🔑 OTP Modal Detected, filling...")
                final_otp = self._get_otp(otp_code)
                await modal_input.fill(final_otp)
                
                confirm_btn = page.locator(".el-message-box__btns button.el-button--primary")
                await confirm_btn.click()
                print("   ✅ OTP Confirmed")
                
        except Exception as e:
             print(f"   [Info] OTP Modal check: {e}")

        await self._wait_for_dashboard(page)

    def _get_otp(self, otp_code_override: str = None) -> str:
        if otp_code_override: return otp_code_override
        if self.totp_secret and "REPLACE" not in self.totp_secret:
            return pyotp.TOTP(self.totp_secret).now()
        raise ValueError("OTP Code required! (No Secret configured and no code provided)")

    async def _wait_for_dashboard(self, page: Page):
        try:
            await page.wait_for_url(lambda u: "login" not in u and len(u.split("/")) > 3, timeout=20000)
            
            context = page.context
            await context.storage_state(path=self.session_path)
            print(f"✅ Login Successful. Session saved to {self.session_path}")
        except Exception as e:
            print(f"❌ Login verification failed (timeout waiting for dashboard). Current URL: {page.url}")
            raise e

    async def close(self):
        pass
