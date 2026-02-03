import os
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime, timedelta

from engine.scripts.core.base_script import BaseScript
from engine.clients.google_sheet import GoogleSheetClient

# --- Strategy Pattern for Agency Parsers ---

class BaseAgencyParser(ABC):
    """Abstract Base Class for parsing agency reports."""
    
    @abstractmethod
    def parse(self, df: pd.DataFrame, target_date: str) -> pd.DataFrame:
        """
        Parse the raw DataFrame into a standardized format.
        Args:
            df: Raw DataFrame from Google Sheet.
            target_date: Target date string 'YYYY-MM-DD'.
        Returns:
            Standardized DataFrame with columns: 
            ['Date', 'Agency', 'Account ID', 'Account Name', 'Payment Amount', 'Cost', 'Cost with Fee']
        """
        pass

class ADCParser(BaseAgencyParser):
    """Parser for ADC Agency (7+1% Fee)."""
    
    def parse(self, df: pd.DataFrame, target_date: str) -> pd.DataFrame:
        # 1. Column Mapping (Based on User Requirements)
        # A: 日期 -> Date
        # B: 打款金额 -> Payment Amount
        # C: 账号ID -> Account ID
        # D: 账号名称 -> Account Name
        # E: 花费（含汇损） -> Cost with Fee
        # G: 花费 -> Cost
        
        # 1. Column Selection by Index (Robust to header errors like #REF!)
        # A(0): Date
        # B(1): Payment Amount
        # E(4): Cost with Fee
        # G(6): Cost
        
        try:
            clean_df = df.iloc[:, [0, 1, 4, 6]].copy()
            clean_df.columns = ['Date', 'Payment Amount', 'Cost with Fee', 'Cost']
        except IndexError:
            raise ValueError(f"ADC Parser Error: Sheet has fewer than 7 columns.")
            
        # Optional Map (Account Level) - specific to details tab, skipped for summary
        # If we need account details later, we'd need a different parser or tab.
        
        # 3. Data Cleaning
        # Convert Date to string YYYY-MM-DD
        clean_df['Date'] = pd.to_datetime(clean_df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Filter by Target Date
        clean_df = clean_df[clean_df['Date'] == target_date].copy()
        
        # Numeric Conversion
        numeric_cols = ['Payment Amount', 'Cost', 'Cost with Fee']
        for col in numeric_cols:
            clean_df[col] = pd.to_numeric(
                clean_df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True), 
                errors='coerce'
            ).fillna(0.0)
            
        # Add Agency Name
        clean_df['Agency'] = 'ADC'
        
        return clean_df

class UDParser(BaseAgencyParser):
    """Parser for UD Agency."""
    
    def parse(self, df: pd.DataFrame, target_date: str) -> pd.DataFrame:
        # UD Mapping (Based on '消耗报表')
        # A: 日期 -> Date
        # B: 打款金额 -> Payment Amount
        # E: 花费 -> Cost with Fee (Confirmed by user: 1.08 * Cost)
        # G: 消耗 -> Cost
        
        column_map = {
            '日期': 'Date',
            '打款金额': 'Payment Amount',
            '花费': 'Cost with Fee',
            '消耗': 'Cost'
        }
        
        missing_cols = [col for col in column_map.keys() if col not in df.columns]
        if missing_cols:
            raise ValueError(f"UD Parser Error: Missing columns {missing_cols}")

        clean_df = df[list(column_map.keys())].rename(columns=column_map)
        
        # Data Cleaning
        clean_df['Date'] = pd.to_datetime(clean_df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        clean_df = clean_df[clean_df['Date'] == target_date].copy()
        
        for col in ['Payment Amount', 'Cost', 'Cost with Fee']:
            clean_df[col] = pd.to_numeric(
                clean_df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True), 
                errors='coerce'
            ).fillna(0.0)
            
        clean_df['Agency'] = 'UD'
        return clean_df

class AgencyParserFactory:
    """Factory to get the correct parser based on template_type."""
    
    @staticmethod
    def get_parser(template_type: str) -> BaseAgencyParser:
        if template_type == 'adc_v1':
            return ADCParser()
        elif template_type == 'ud_v1':
            return UDParser()
        else:
            raise ValueError(f"Unknown template_type: {template_type}")

# --- Main Business Script ---

class AgencyReconciliationScript(BaseScript):
    DOMAIN = "marketing"
    JOB_NAME = "ad_spend_reconciliation"
    
    def run(self):
        # 1. Load Config
        recon_config = self.config.get('domain', {}).get('marketing', {}).get('acquisition', {}).get('reconciliation')
        if not recon_config:
            self.logger.error("No reconciliation config found for this app.")
            return

        agencies = recon_config.get('agencies', {})
        output_dir = recon_config.get('output_dir', 'marketing/acquisition')
        
        # Target Date: Yesterday (default)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.logger.info(f"🚀 Starting Ad Spend Reconciliation for Date: {yesterday}")

        all_data = []
        gs_client = GoogleSheetClient(self.config)

        # 2. Iterate Agencies
        for agency_name, config in agencies.items():
            try:
                self.logger.info(f"Processing Agency: {agency_name}...")
                
                # Fetch Data
                sheet_url = config['source_sheet_url']
                tab_name = config.get('sheet_tab_name', '消耗报表')
                template_type = config.get('template_type')
                
                self.logger.info(f"  - Reading Sheet: {sheet_url} (Tab: {tab_name})")
                    
                raw_df = gs_client.read_as_dataframe(sheet_url, worksheet_name=tab_name)
                
                if raw_df.empty:
                    self.logger.warning(f"  - Sheet is empty or failed to load.")
                    continue

                # Parse Data
                parser = AgencyParserFactory.get_parser(template_type)
                clean_df = parser.parse(raw_df, yesterday)
                
                count = len(clean_df)
                total_cost = clean_df['Cost'].sum() if not clean_df.empty else 0
                self.logger.info(f"  - Parsed {count} records. Total Cost: {total_cost}")
                
                if not clean_df.empty:
                    all_data.append(clean_df)

            except Exception as e:
                self.logger.error(f"❌ Failed to process agency {agency_name}: {e}")

        # 3. Aggregation & Output
        if not all_data:
            self.logger.warning("⚠️ No data found for yesterday. Skipping report generation.")
            return

        # Preview Notification in Dry Run
        if self.dry_run:
            self._send_notification(yesterday, all_data)
            self.logger.info("✅ [Dry Run] Reconciliation Logic Verified. No files written.")
            return
            
        final_df = pd.concat(all_data, ignore_index=True)
        
        # Sort columns
        final_cols = ['Date', 'Agency', 'Account ID', 'Account Name', 'Payment Amount', 'Cost', 'Cost with Fee']
        # Handle cases where some cols might be missing in other parsers (future proofing)
        for col in final_cols:
            if col not in final_df.columns:
                final_df[col] = 0
        final_df = final_df[final_cols]
        
        # Save to File
        file_name = f"daily_ad_spend_{yesterday.replace('-', '')}.csv"
        out_path = self.out.get_path(file_name)
        final_df.to_csv(out_path, index=False)
        
        self.logger.info(f"🎉 Report Generated: {out_path}")
        self.logger.info(f"Total Records: {len(final_df)}")
        self.logger.info(f"Total Cost: {final_df['Cost'].sum()}")
        
        # 4. Notify (Lark)
        self._send_notification(yesterday, all_data)
        
    def _send_notification(self, date_str: str, dfs: List[pd.DataFrame]):
        """Constructs and sends the daily summary report."""
        if not dfs:
             return

        # Aggregate Total
        all_df = pd.concat(dfs, ignore_index=True)
        total_payment = all_df['Payment Amount'].sum()
        total_cost_fee = all_df['Cost with Fee'].sum()
        total_cost_raw = all_df['Cost'].sum()
        
        # Aggregate per Agency
        agency_stats = all_df.groupby('Agency').agg({
            'Payment Amount': 'sum',
            'Cost with Fee': 'sum'
        }).reset_index()
        
        # Build Message
        lines = []
        lines.append(f"📅 **日期**: {date_str}")
        lines.append(f"💰 **总打款**: ${total_payment:,.2f}")
        lines.append(f"💸 **总花费 (含服务费)**: ${total_cost_fee:,.2f}")
        lines.append(f"📉 **总花费 (原始)**: ${total_cost_raw:,.2f}")
        lines.append("")
        lines.append("------------------")
        
        for _, row in agency_stats.iterrows():
            lines.append(f"**{row['Agency']}**:")
            lines.append(f"  • 打款: ${row['Payment Amount']:,.2f}")
            lines.append(f"  • 花费 (含费): ${row['Cost with Fee']:,.2f}")
            lines.append("")
            
        msg = "\n".join(lines)
        
        if self.dry_run:
            self.logger.info(f"📢 [Dry Run] Notification Content Preview:\n{msg}")
            return
        
        # Send via Notifier
        # Routing Key: marketing.acquisition.reconciliation -> marketing_recon_channel (Lark Webhook)
        self.notifier.send(
            title=f"📢 Daily Ad Spend Reconciliation - {self.args.app.upper()}",
            message=msg,
            key="marketing.acquisition.reconciliation"
        )

if __name__ == "__main__":
    AgencyReconciliationScript().execute()
