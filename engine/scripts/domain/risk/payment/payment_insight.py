import numpy as np
import sys
import pandas as pd
import datetime
import yaml
from pathlib import Path
from dateutil.relativedelta import relativedelta

# Add engine to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from engine.scripts.core.base_script import BaseScript
from engine.clients.gemini import GeminiClient
from engine.clients.google_drive import GoogleDriveClient

class PaymentInsightScript(BaseScript):
    DOMAIN = "risk"
    SUB_DOMAIN = "payment"
    JOB_NAME = "payment_insight"
    
    def add_arguments(self, parser):
        parser.add_argument("--period", type=str, default="yesterday", choices=["yesterday", "today"], help="Analysis Period: 'yesterday' (Daily Report) or 'today' (Intraday)")

    def run(self):
        app_name = self.args.app
        app_id = self.config.get('datasources', {}).get('app_id', 0)
        period = self.args.period
        
        self.logger.info(f"🚀 Starting Payment Insight ({period.upper()}) for App: {app_name} (ID: {app_id})")
        
        # Initialize Connector
        self.connector = self.get_connector('doris')
        
        if period == "yesterday":
            self._run_daily(app_name, app_id)
        else:
            self._run_intraday(app_name, app_id)

    def _run_daily(self, app_name, app_id):
        # 1. Load SQL Config
        sql_cfg_path = self.paths.knowledge_root / "reports" / "risk" / "payment" / "payment_insight_daily.yaml"
        with open(sql_cfg_path, 'r') as f:
            sql_cfg = yaml.safe_load(f)
            
        # 2. Date Calculation
        t_now = datetime.datetime.now()
        t_yesterday = t_now - datetime.timedelta(days=1)
        start_time = t_yesterday.strftime("%Y-%m-%d 00:00:00")
        end_time = t_now.strftime("%Y-%m-%d 00:00:00")
        t_baseline = t_yesterday - datetime.timedelta(days=7)
        baseline_start = t_baseline.strftime("%Y-%m-%d 00:00:00")
        
        params = {
            "app_id": app_id,
            "start_time": start_time,
            "end_time": end_time,
            "baseline_start": baseline_start
        }
        
        self.logger.info(f"📅 Daily Time Range: {start_time} to {end_time}")

        # 3. Extract Data
        # Yesterday
        sql_yesterday = self._inject_params(sql_cfg['queries']['yesterday_stats'], params)
        df_yesterday = self.connector.query(sql_yesterday)
        
        # Baseline
        sql_baseline = self._inject_params(sql_cfg['queries']['baseline_stats'], params)
        df_baseline = self.connector.query(sql_baseline)
        
        if df_yesterday.empty:
            self.logger.warning("No data for yesterday.")
            return

        # 4. Transform
        self._process_and_deliver(app_name, df_yesterday, df_baseline, t_yesterday, "daily")

    def _run_intraday(self, app_name, app_id):
        # 1. Load SQL Config
        sql_cfg_path = self.paths.knowledge_root / "reports" / "risk" / "payment" / "payment_insight_intraday.yaml"
        with open(sql_cfg_path, 'r') as f:
            sql_cfg = yaml.safe_load(f)
            
        # 2. Date Calculation
        t_now = datetime.datetime.now()
        t_today_start = t_now.strftime("%Y-%m-%d 00:00:00")
        
        t_yesterday = t_now - datetime.timedelta(days=1)
        t_yesterday_start = t_yesterday.strftime("%Y-%m-%d 00:00:00")
        t_yesterday_same_time = t_yesterday.strftime("%Y-%m-%d %H:%M:%S")
        
        params = {
            "app_id": app_id,
            "today_start": t_today_start,
            "current_time": t_now.strftime("%Y-%m-%d %H:%M:%S"),
            "yesterday_start": t_yesterday_start,
            "yesterday_same_time": t_yesterday_same_time
        }
        
        self.logger.info(f"⏱️ Intraday Time Range: {t_today_start} to NOW vs Yesterday Same-Time")

        # 3. Extract Data
        # Today
        sql_today = self._inject_params(sql_cfg['queries']['today_stats'], params)
        df_today = self.connector.query(sql_today)
        
        # Yesterday Same Time
        sql_yesterday = self._inject_params(sql_cfg['queries']['yesterday_same_time_stats'], params)
        df_yesterday_baseline = self.connector.query(sql_yesterday)
        
        if df_today.empty:
            self.logger.warning("No data for today yet.")
            return

        # 4. Transform (Reuse logic but mapping columns)
        # Rename baseline columns to match standard baseline format expected by _process_and_deliver logic?
        # Actually _process_and_deliver expects df_primary and df_baseline.
        # df_yesterday_baseline has cols: total_orders_yesterday, success_count_yesterday
        # We need to map them to standard baseline names if we want to reuse logic, OR update logic.
        # Let's align dataframe columns to standard expectations:
        df_yesterday_baseline = df_yesterday_baseline.rename(columns={
            "total_orders_yesterday": "total_orders_7d", # Hack to reuse '7d' logic var name, logically it is 'baseline'
            "success_count_yesterday": "success_count_7d"
        })
        
        self._process_and_deliver(app_name, df_today, df_yesterday_baseline, t_now, "intraday")

    def _process_and_deliver(self, app_name, df_primary, df_baseline, date_obj, mode="daily"):
        # 4. Transform Data (Pandas Logic)
        processor = PaymentDataProcessor()
        
        # Process Primary
        df_processed = processor.process_raw_data(df_primary)
        
        # Process Baseline (for comparison)
        df_base_processed = processor.process_raw_data(df_baseline, is_baseline=True)
        
        # Aggregate logic
        df_summary = processor.aggregate_summary(df_processed)
        df_details = processor.aggregate_details(df_processed)
        df_base_details = processor.aggregate_details(df_base_processed, prefix="7d_")
        
        # Merge Baseline into Details
        df_final_details = pd.merge(
            df_details,
            df_base_details[['route_type', 'sub_channel_norm', 'pay_method', '7d_success_rate_pct', '7d_total_orders']],
            on=['route_type', 'sub_channel_norm', 'pay_method'],
            how='left'
        )
        # Calculate Delta
        df_final_details['sr_delta'] = df_final_details['success_rate_pct'] - df_final_details['7d_success_rate_pct']

        # 5. Load / Export (Multi-Output)
        output_dir = self.paths.get_output_root(self.DOMAIN, self.SUB_DOMAIN) / app_name / date_obj.strftime("%Y-%m")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        suffix = mode
        summary_path = output_dir / f"payment_summary_{date_obj.strftime('%Y%m%d')}_{suffix}.csv"
        df_summary.to_csv(summary_path, index=False)
        
        details_path = output_dir / f"payment_details_{date_obj.strftime('%Y%m%d')}_{suffix}.csv"
        df_final_details.to_csv(details_path, index=False)
        
        self.logger.info(f"💾 Data saved to:\n  - {summary_path}")
        
        # 5.1 Upload to Google Drive (if configured)
        drive_links = {}
        folder_id = self.config.get('google_drive', {}).get('payment_risk_folder_id')
        
        if folder_id:
            try:
                # Intraday might skip drive upload to save API quota? OR upload to a 'Temp' folder?
                # User didn't specify, but for safety let's upload.
                self.logger.info(f"🚀 Uploading to Google Drive...")
                drive = GoogleDriveClient(self.config)
                
                f_sum = drive.upload_file(str(summary_path), folder_id=folder_id)
                drive_links['Summary'] = f_sum.get('webViewLink')
                
                f_det = drive.upload_file(str(details_path), folder_id=folder_id)
                drive_links['Details'] = f_det.get('webViewLink')
            except Exception as e:
                self.logger.error(f"❌ Google Drive Upload Failed: {e}")

        # 6. Prepare AI Prompt
        df_top_movers = df_final_details.sort_values('total_orders', ascending=False).head(20)
        data_text = f"## Overall Performance\n{df_summary.to_markdown(index=False)}\n\n## Top Channels Detail\n{df_top_movers.to_markdown(index=False)}"
        
        self._run_ai_analysis(app_name, date_obj, data_text, details_path, drive_links, mode)

    def _inject_params(self, sql, params):
        for k, v in params.items():
            sql = sql.replace(f"{{{{{k}}}}}", str(v))
        return sql

    def _run_ai_analysis(self, app_name, date_obj, data_text, csv_path, drive_links=None, mode="daily"):
        prompt_file = "payment_insight_daily.yaml" # default logic fallback? 
        # Actually mapping mode to prompt file
        if mode == "intraday":
             prompt_name = "intraday_payment_insight.md"
        else:
             prompt_name = "daily_payment_insight.md"
             
        prompt_path = self.paths.knowledge_root / "prompts" / "risk" / "payment" / prompt_name
        if not prompt_path.exists():
            self.logger.error(f"Prompt template not found at {prompt_path}")
            return

        with open(prompt_path, 'r') as f:
            template = f.read()
            
        time_str = date_obj.strftime('%Y-%m-%d %H:%M') if mode == "intraday" else date_obj.strftime('%Y-%m-%d')
        prompt = template.replace("{{app_name}}", app_name)\
                         .replace("{{date}}", time_str)\
                         .replace("{{time}}", time_str)\
                         .replace("{{data_table}}", data_text)
        
        self.logger.info("🧠 Requesting Gemini Analysis (Model: gemini-3-pro-preview)...")
        gemini = GeminiClient(self.config, model="gemini-3-pro-preview")
        analysis_text = gemini.generate_content(prompt) or "⚠️ Analysis Failed."

        # Send Notification
        self._send_notification(app_name, date_obj, analysis_text, csv_path, drive_links, mode)

    def _send_notification(self, app_name, date_obj, analysis, csv_path, drive_links=None, mode="daily"):
        if mode == "intraday":
            title_emoji = "🚨" if "alert" in analysis.lower() or "urgent" in analysis.lower() else "⏱️"
            title = f"{title_emoji} 日内支付预警: {app_name}"
            date_str = date_obj.strftime('%Y-%m-%d %H:%M')
        else:
            title = f"每日支付洞察: {app_name}"
            date_str = date_obj.strftime('%Y-%m-%d')
            
        full_message = f"**{title}**\n📅 Time: {date_str}\n"
        full_message += "--------------------------------\n"
        full_message += analysis
        full_message += f"\n--------------------------------\n"
        
        if drive_links and drive_links.get('Details'):
            full_message += f"📥 [Download Details (Google Drive)]({drive_links['Details']})"
        else:
            full_message += f"📥 [Download Details (Local)]({csv_path})"
        
        self.notifier.send(
            title=title,
            message=full_message,
            key="risk.payment"
        )

class PaymentDataProcessor:
    """Encapsulates Pandas transformation logic for Payment domain."""
    
    def process_raw_data(self, df: pd.DataFrame, is_baseline=False) -> pd.DataFrame:
        """Raw Logs -> Normalized Data"""
        if df.empty:
            return df
            
        df = df.copy()
        
        # 1. Route Classification (Vectorized)
        # 7 = OnePay, Others = Direct
        df['route_type'] = np.where(df['recharge_channel'] == 7, 'OnePay', 'Direct')
        
        # 2. Sub-Channel Normalization
        # Clean 'upstream_channel' (e.g. remove suffixes if needed, or unify names)
        # For now, we assume simple cleaning or pass-through
        # Example: 'PlusPay_01' -> 'PlusPay' (Regex if needed)
        df['sub_channel_norm'] = df['upstream_channel'].fillna('Unknown')
        
        # 3. Type Conversion
        df['total_orders'] = pd.to_numeric(df['total_orders'] if not is_baseline else df['total_orders_7d'])
        df['success_count'] = pd.to_numeric(df['success_count'] if not is_baseline else df['success_count_7d'])
        
        return df

    def aggregate_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates by Route + PayMethod (High Level)"""
        # Group
        g = df.groupby(['route_type', 'pay_method']).agg({
            'total_orders': 'sum',
            'success_count': 'sum'
        }).reset_index()
        
        # Calculate Metrics
        return self._calc_metrics(g)

    def aggregate_details(self, df: pd.DataFrame, prefix="") -> pd.DataFrame:
        """Aggregates by SubChannel (Provider Level)"""
        # Group by Normalized Channel
        g = df.groupby(['route_type', 'sub_channel_norm', 'pay_method']).agg({
            'total_orders': 'sum',
            'success_count': 'sum',
            # Avg Latency only for primary data (not baseline usually, unless simple avg)
            # keeping simple for now
        }).reset_index()
        
        # Calculate Metrics
        res = self._calc_metrics(g)
        
        if prefix:
            res = res.add_prefix(prefix)
            # Rename keys back for joining
            res = res.rename(columns={
                f"{prefix}route_type": "route_type",
                f"{prefix}sub_channel_norm": "sub_channel_norm", 
                f"{prefix}pay_method": "pay_method"
            })
            
        return res

    def _calc_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Shared Metric Calculation"""
        # Success Rate
        df['success_rate_pct'] = (df['success_count'] / df['total_orders'] * 100).round(2)
        
        # Order Share
        total_vol = df['total_orders'].sum()
        if total_vol > 0:
            df['order_share_pct'] = (df['total_orders'] / total_vol * 100).round(2)
        else:
            df['order_share_pct'] = 0.0
            
        return df

if __name__ == "__main__":
    PaymentInsightScript().execute()
