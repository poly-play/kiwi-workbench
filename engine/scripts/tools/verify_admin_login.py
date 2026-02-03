import asyncio
from engine.scripts.core.base_script import BaseScript
from engine.drivers.admin_panel import AdminPanelDriver

class VerifyAdminLogin(BaseScript):
    JOB_NAME = "verify_admin_login"
    DOMAIN = "tech"
    SUB_DOMAIN = "tools"
    
    def add_arguments(self, parser):
        parser.add_argument("--otp", help="Manual Google Authenticator Code")
        parser.add_argument("--headless", action="store_true", help="Run in headless mode (default: False for debug)")

    def run(self):
        # BaseScript already loads config based on --app/--env/--region
        # and handles ArgParsing (including --dry-run)
        
        # Override headless if flag set
        if self.args.headless:
            self.config['admin_panel']['headless'] = True
            
        print(f"🔄 verifying Admin Login for: {self.args.app}")
        print(f"   URL: {self.config['admin_panel'].get('url')}")
        
        # Async wrapper for synchronous run()
        async def _async_run():
            driver = AdminPanelDriver(self.config)
            try:
                # [DRY RUN CHECK]
                if self.dry_run:
                    print(f"⚠️  [DRY RUN] Would attempt login to {self.config['admin_panel'].get('url')}")
                    print(f"   User: {driver.username}")
                    return {"status": "dry_run_success"}

                page = await driver.login(otp_code=self.args.otp)
                title = await page.title()
                url = page.url
                print(f"✅ Login Success!")
                print(f"   Title: {title}")
                print(f"   URL: {url}")
                
                # Take Screenshot
                screenshot_path = "login_success.png"
                await page.screenshot(path=screenshot_path)
                print(f"📸 Screenshot saved to {screenshot_path}")
                
            except Exception as e:
                raise e
            finally:
                await driver.close()
                
            return {"status": "success", "title": title}

        # Run async loop
        return asyncio.run(_async_run())

if __name__ == "__main__":
    VerifyAdminLogin().execute()
