import datetime
import sys
import pandas as pd
from pathlib import Path

# Add engine to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Imports after sys.path fix
from engine.scripts.core.base_script import BaseScript
from engine.clients.google_sheet import GoogleSheetClient

class AgencyReconciliationScript(BaseScript):
    DOMAIN = "marketing"
    SUB_DOMAIN = "acquisition"
    JOB_NAME = "agency_reconciliation"
    
    def add_arguments(self, parser):
        parser.add_argument("--date", type=str, default=None, help="Date to reconcile (YYYY-MM-DD). Defaults to yesterday.")
        parser.add_argument("--agency", type=str, default=None, help="Filter by Agency Name (e.g., ADC)")
        parser.add_argument("--discover", action="store_true", help="Discovery Mode: Prints columns of source sheets without processing.")

    def run(self):
        # BaseScript loads merged config into self.config
        # We look for domain.marketing.acquisition.reconciliation
        
        mkt_config = self.config.get('domain', {}).get('marketing', {}).get('acquisition', {}).get('reconciliation', {})
        
        if not mkt_config:
            self.logger.error("No reconciliation config found for this app environment. Check config.yaml")
            return

        self.gs_client = GoogleSheetClient(self.config)
        summary_url = mkt_config.get('summary_sheet_url')
        
        target_date = self._get_target_date()
        self.logger.info(f"🚀 Starting Reconciliation for Date: {target_date}")
        
        agencies = mkt_config.get('agencies', {})
        for agency_name, agency_data in agencies.items():
            if self.args.agency and self.args.agency != agency_name:
                continue
                
            for channel_name, channel_data in agency_data.get('channels', {}).items():
                self._process_channel(agency_name, channel_name, channel_data, summary_url, target_date)

    def _get_target_date(self):
        if self.args.date:
            return self.args.date
        return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    def _process_channel(self, agency, channel, channel_data, summary_url, target_date):
        source_url = channel_data.get('source_sheet_url')
        app_name = self.args.app
        
        self.logger.info(f"Processing {agency} - {channel}...")
        
        try:
            # READ Source
            df_source = self.gs_client.read_as_dataframe(source_url) 
            
            if self.args.discover:
                self.logger.info(f"🔍 [DISCOVERY] Columns for {agency}-{channel}: {list(df_source.columns)}")
                # Also print first row for context
                if not df_source.empty:
                     self.logger.info(f"   Sample Row: {df_source.iloc[0].to_dict()}")
                return

            # RECONCILIATION LOGIC
            
            # 1. Normalize Date Header
            DATE_COL = '日期'
            SPEND_COL = '消耗'
            
            if DATE_COL not in df_source.columns or SPEND_COL not in df_source.columns:
                msg = f"❌ Missing required columns in {agency}-{channel}. Found: {list(df_source.columns)}"
                self.logger.error(msg)
                self._send_alert(app_name, agency, channel, target_date, msg, level="error")
                return

            # 2. Filter Date
            df_source[DATE_COL] = df_source[DATE_COL].astype(str)
            row = df_source[df_source[DATE_COL] == target_date]
            
            if row.empty:
                msg = f"⚠️ No data found for {target_date} in {agency}-{channel}."
                self.logger.warning(msg)
                self._send_alert(app_name, agency, channel, target_date, msg, level="warning")
                return
            
            # 3. Extract Data
            # Assuming first match is correct
            record = row.iloc[0]
            actual_spend_str = str(record.get(SPEND_COL, '0')).replace(',', '')
            try:
                actual_spend = float(actual_spend_str)
            except ValueError:
                actual_spend = 0.0
                
            service_fee = 0.0 # Not present in source, assumed 0 for now or handled by summary sheet formulas?
            # User requirement: Aggregate Actual Spend, Service Fee, Total Spend
            total_spend = actual_spend + service_fee
            
            self.logger.info(f"✅ Found Data: Spend={actual_spend}")
            
            # 4. Append to Summary
            # Columns: Date, Agency, Channel, Actual Spend, Service Fee, Total Spend
            row_data = [target_date, agency, channel, actual_spend, service_fee, total_spend]
            
            if not self.dry_run:
                self.gs_client.append_row(summary_url, row_data)
                self.logger.info(f"Written to Summary: {row_data}")
                self._send_alert(app_name, agency, channel, target_date, "Success", detail=f"Written Rows: {row_data}")
            else:
                self.logger.info(f"[DRY RUN] Would write: {row_data}")
                self._send_alert(app_name, agency, channel, target_date, "Dry Run Success", detail=f"Data Found: {row_data}")

        except Exception as e:
            self.logger.error(f"Error processing {agency}-{channel}: {e}")
            self._send_alert(app_name, agency, channel, target_date, f"Exception: {str(e)}", level="error")

    def _send_alert(self, app, agency, channel, date, message, detail="", level="info"):
        title = f"📢 Marketing Reconciliation: {agency}-{channel}"
        if level == "error":
            title = f"🚨 {title} (Failed)"
        elif level == "warning":
            title = f"⚠️ {title} (Warning)"
            
        full_msg = f"**App**: {app}\n**Date**: {date}\n**Status**: {message}\n"
        if detail:
            full_msg += f"\n**Details**:\n{detail}"
            
        # Use marketing.acquisition key -> routes to marketing_reconciliation_group
        self.notifier.send(
            title=title,
            message=full_msg,
            key="marketing.acquisition"
        )

if __name__ == "__main__":
    AgencyReconciliationScript().execute()
