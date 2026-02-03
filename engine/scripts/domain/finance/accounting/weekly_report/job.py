import sys
from pathlib import Path

# Add engine to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from engine.scripts.core.base_script import BaseScript
from engine.scripts.domain.finance.accounting.weekly_report.sources import ALL_SOURCES

class UnifiedWeeklyReportJob(BaseScript):
    DOMAIN = "finance"
    SUB_DOMAIN = "accounting" 
    JOB_NAME = "weekly_report_unified"

    def _setup_args(self):
        # Override to make app optional or default to 'unified'
        super()._setup_args()
        # Not strictly enforcing app if we don't want to, but BaseScript might add it.
        # Ideally we just pass a dummy app in command line or override parsing if BaseScript is rigid.
        # But BaseScript usually adds arguments. Let's just run with --app unified in command line.
        pass

    def run(self):
        self.logger.info("🚀 Starting Unified Weekly Report Job")
        
        results = []
        for SourceClass in ALL_SOURCES:
            source = SourceClass()
            self.logger.info(f"🔄 Processing Source: {source.app_name}")
            try:
                data = source.get_weekly_data()
                results.append(data)
                self.logger.info(f"✅ Success: {source.app_name}")
            except Exception as e:
                self.logger.error(f"❌ Failed: {source.app_name} - {e}", exc_info=True)
                
        if not results:
            self.logger.warning("⚠️ No results generated.")
            return

        # Build Report Content
        report_content = self._build_report_content(results)
        
        # Output to Console (for Logs)
        self.logger.info("\n" + report_content)
        
        # Send Notification
        # We manually construct the notification content to ensure the format is preserved
        # The BaseScript notification might wrap it differently, but passing the string as 'message' usually works.
        # However, for tables, we rely on the BaseScript's Lark formatter if possible, 
        # but here we have a custom multi-section format.
        # Let's send it as a standard notification with the constructed text.
        
        # Note: BaseScript.execute() handles the notification via self._send_notification() usually on failure.
        # But we want to send success report.
        # We can implement a custom send method or just rely on the logging if we want to pipe it.
        # But per requirements, "Unified Task -> Lark".
        # Let's use the notification client directly or valid hook.
        
        # For now, we print it. The 'BaseScript' usually sends email/lark if configured?
        # Actually in this codebase, BaseScript doesn't auto-send SUCCESS notifications by default 
        # unless configured or if we call a specific method.
        # Let's use the user's notification pattern (Lark Webhook).
        # We'll use the 'risk.payment' channel as configured previously or 'finance.accounting'.
        
        self.send_custom_notification(report_content)

    def send_custom_notification(self, content):
        """Sends the unified report to the configured Lark webhook."""
        if hasattr(self, 'notifier'):
            # Construct Title
            # Use Routing Key for Risk/Payment or Accounting
            # User previously used 'finance.accounting'.
            
            self.notifier.send(
                key="finance.accounting", 
                title=f"📊 财务周报汇总 (Consolidated Weekly Report)",
                message=content,
                level="info"
            )
        else:
            self.logger.warning("Notifier not available.")

    def _build_report_content(self, results):
        """Formats the data into Per-App Blocks."""
        lines = []
        
        # 1. Global Header
        if results:
            dr = results[0]['date_range']
            header = f"📅 **周运营综述** ({dr['start']} ~ {dr['end']})"
            lines.append(header)
            lines.append("")
        
        # 2. Per App Block
        for r in results:
            app = r['app_name']
            curr = r['last_week']
            prev = r['prev_week']
            cum = r['cumulative']
            
            # Header
            lines.append(f"🟢 **{app}**")
            
            # Cumulative Summary Line
            cum_line = (
                f"**累计:** "
                f"消耗 {self._fmt_large(cum['spend'], is_currency=True)} | "
                f"订单 {self._fmt_large(cum['orders'], is_currency=False)} | "
                f"成本 ${cum['cpa']:.2f}"
            )
            lines.append(cum_line)
            lines.append("----------------------------------")
            
            # Weekly Details with WoW
            lines.append(f"- **消耗 (Spend)**: {self._fmt_detail(curr['spend'], prev['spend'], is_currency=True)}")
            lines.append(f"- **订单 (Orders)**: {self._fmt_detail(curr['orders'], prev['orders'])}")
            lines.append(f"- **获客成本 (CPA)**: {self._fmt_detail(curr['cpa'], prev['cpa'], is_currency=True)}")
            lines.append(f"- **净充值 (Net Deposit)**: {self._fmt_detail(curr['net_deposit'], prev['net_deposit'], is_currency=True)}")
            lines.append(f"- **毛利 (Gross Profit)**: {self._fmt_detail(curr['gross_profit'], prev['gross_profit'], is_currency=True)}")
            
            # [NEW] Missing Data Alert
            if r.get('missing_spend_dates'):
                 dates_str = ", ".join(r['missing_spend_dates'])
                 lines.append(f"⚠️ **数据缺失提醒**: {dates_str} 花费为 0")
            
            lines.append("")
            
        return "\n".join(lines)

    def _fmt_currency(self, val):
        if val >= 1000000: return f"${val/1000000:.2f}M"
        if val >= 1000: return f"${val/1000:.1f}k"
        return f"${val:,.0f}"

    def _fmt_num(self, val):
        if val >= 1000000: return f"{val/1000000:.2f}M"
        if val >= 1000: return f"{val/1000:.1f}k"
        return f"{val:,.0f}"
        
    def _fmt_large(self, val, is_currency=True):
        # Always M for cumulative if large
        val_str = f"{val/1000000:.1f}M"
        
        if val >= 1000000:
             return f"${val_str}" if is_currency else val_str
        
        # Fallback
        if is_currency:
            return self._fmt_currency(val)
        return self._fmt_num(val)

    def _fmt_detail(self, curr, prev, is_currency=False):
        # Format: $9,731 (📉-37%)
        if prev == 0:
            wow = "N/A"
            icon = ""
        else:
            diff = (curr - prev) / prev
            pct = diff * 100
            icon = "📈" if diff > 0 else "📉"
            wow = f"{icon}{pct:+.1f}%"
            
        val_str = f"${curr:,.2f}" if is_currency else f"{curr:,.0f}"
        return f"{val_str} ({wow})"

if __name__ == "__main__":
    UnifiedWeeklyReportJob().execute()
