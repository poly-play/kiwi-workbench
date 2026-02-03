import pandas as pd
import datetime
from engine.clients.google_sheet import GoogleSheetClient

class OperationsDataProcessor:
    """Encapsulates Pandas Clean-up & Calculation Logic."""
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # 1. Fix Headers (Row 0 is usually junk config, Row 1 is headers)
        if len(df) > 1:
            real_headers = df.iloc[0]
            df = df[1:].copy()
            df.columns = real_headers
            df.columns = df.columns.astype(str).str.strip()
        
        # Map Columns (Chinese -> English)
        rename_map = {
            '日期': 'Date',
            '消耗': 'Spend',
            '累计消耗': 'CumSpend',
            '首充人数': 'Orders',
            '累计总首充': 'CumOrders', # Usually inaccurate in sheet, checking logic below
            '实际冲提（USD)': 'NetDeposit'
        }
        df = df.rename(columns=rename_map)
        
        # Clean Date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']) 
        
        # Clean Numeric Columns (Remove '$', ',')
        cols_to_clean = ['Spend', 'Orders', 'NetDeposit', 'CumSpend', 'CumOrders']
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.replace('%', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df

    def calc_weekly_metrics(self, df: pd.DataFrame) -> dict:
        total_spend = df['Spend'].sum()
        total_orders = df['Orders'].sum()
        total_net = df['NetDeposit'].sum()
        
        # Calculated
        # CPA = Spend / Orders
        cpa = total_spend / total_orders if total_orders > 0 else 0
        
        # Profit = Net Deposit - Spend (User definition)
        gross_profit = total_net - total_spend
        
        return {
            "spend": total_spend,
            "orders": total_orders,
            "cpa": cpa,
            "net_deposit": total_net,
            "gross_profit": gross_profit
        }

    def calc_cumulative_metrics(self, df: pd.DataFrame) -> dict:
        """Calculates cumulative metrics specific to India Logic."""
        metrics_cum = {}
        if not df.empty:
            # India Sheet has explicit 'CumSpend' column which is accurate
            metrics_cum["spend"] = df['CumSpend'].max() if 'CumSpend' in df.columns else 0
            # India Sheet 'CumOrders' is inaccurate, so we sum daily 'Orders'
            metrics_cum["orders"] = df['Orders'].sum()
        else:
            metrics_cum["spend"] = 0
            metrics_cum["orders"] = 0
            
        metrics_cum["cpa"] = metrics_cum["spend"] / metrics_cum["orders"] if metrics_cum["orders"] > 0 else 0
        return metrics_cum

class BaseWeeklySource:
    """Abstract Base Class (ABC) for Weekly Report Sources."""
    
    def __init__(self, sheet_id: str, app_name: str, sheet_gid: int = None, processor=None):
        self.sheet_id = sheet_id
        self.app_name = app_name
        self.sheet_gid = sheet_gid # If None, reads first sheet. If Int, reads specific GID/Index.
        # Default to India Processor if none provided
        self.processor = processor if processor else OperationsDataProcessor()
        
    def get_weekly_data(self):
        """Fetches data, calculates Last Week, Prev Week, and Cumulative metrics."""
        gs = GoogleSheetClient()
        # Read Sheet
        url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"
        
        # Pass GID explicitly if present
        if self.sheet_gid is not None:
             df = gs.read_as_dataframe(url, worksheet_gid=self.sheet_gid)
        else:
             df = gs.read_as_dataframe(url)
             
        # Delegate cleaning to the specific processor
        # The processor is responsible for handling headers/indices
        df = self.processor.clean_data(df)
        
        # 3. Determine Date Range
        today = datetime.date.today()
        # Last Week (Mon-Sun)
        last_week_start = today - datetime.timedelta(days=today.weekday() + 7)
        last_week_end = last_week_start + datetime.timedelta(days=6)
        
        # Prev Week
        prev_week_start = last_week_start - datetime.timedelta(days=7)
        prev_week_end = last_week_start - datetime.timedelta(days=1)
        
        # 4. Filter
        df_last_week = df[(df['Date'].dt.date >= last_week_start) & (df['Date'].dt.date <= last_week_end)]
        df_prev_week = df[(df['Date'].dt.date >= prev_week_start) & (df['Date'].dt.date <= prev_week_end)]
        
        # 5. Calculate Metrics
        metrics_last = self.processor.calc_weekly_metrics(df_last_week)
        metrics_prev = self.processor.calc_weekly_metrics(df_prev_week)
        
        # 6. Cumulative
        # Delegate cumulative extraction to processor if custom logic needed?
        # Default logic: Use Max of CumSpend/CumOrders if columns exist, else Sum of Daily?
        # India Processor has specific logic.
        # Let's standardize: Processor should return cumulative stats or we calculated here.
        # To avoid breaking India logic which mixes 'CumSpend' column and 'Orders' sum.
        # Let's add a `calc_cumulative_metrics(df)` to the Processor interface.
        
        if hasattr(self.processor, 'calc_cumulative_metrics'):
            metrics_cum = self.processor.calc_cumulative_metrics(df)
        else:
            # Fallback/Legacy Logic (moved from before)
            metrics_cum = {}
            if not df.empty:
                metrics_cum["spend"] = df['CumSpend'].max() if 'CumSpend' in df.columns else df['Spend'].sum()
                metrics_cum["orders"] = df['Orders'].sum()
            else:
                metrics_cum["spend"] = 0
                metrics_cum["orders"] = 0
            metrics_cum["cpa"] = metrics_cum["spend"] / metrics_cum["orders"] if metrics_cum["orders"] > 0 else 0
        
        # 7. Check for missing spend (New Alert)
        missing_dates = []
        if not df_last_week.empty:
            # Check rows where Spend is 0 or less (assuming valid spend is positive)
            # Use 'Spend' column.
            # Convert to list of string YYYY-MM-DD
            zero_spend = df_last_week[df_last_week['Spend'] <= 0]
            if not zero_spend.empty:
                missing_dates = zero_spend['Date'].dt.strftime('%Y-%m-%d').tolist()

        return {
            "app_name": self.app_name,
            "last_week": metrics_last,
            "prev_week": metrics_prev,
            "cumulative": metrics_cum,
            "missing_spend_dates": missing_dates,
            "date_range": {
                "start": last_week_start,
                "end": last_week_end
            }
        }
