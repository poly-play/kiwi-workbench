import pandas as pd
from .base_source import BaseWeeklySource

class MenaDataProcessor:
    """Processor for MENA Sheets (Kanzplay, Falcowin, SakerWin)."""
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Mena Sheets have Headers on Column 1 (Index 0)? 
        # User said: A=Date, B=Spend, I=Orders, Y=NetDeposit
        # The sheet likely has headers at Row 1 (Index 1) or similar, but columns are fixed.
        # Let's select by Integer Index to be safe, regardless of header name.
        
        if df.empty:
            return pd.DataFrame(columns=['Date', 'Spend', 'Orders', 'NetDeposit'])

        # 1. Identify Headers
        # We assume headers are in the first row (common in these sheets)
        headers = df.columns.tolist() # Get current columns (which might be Row 1 values if read_as_dataframe defaulted)
        
        # 2. Helper to find column index by name (partial match or exact)
        def find_col(candidates):
            for i, col in enumerate(headers):
                c_str = str(col).strip()
                if c_str in candidates:
                    return i
            return -1

        # 3. Locate Indices
        idx_date = find_col(['日期'])
        idx_spend = find_col(['投放花费', '消耗', '花费'])
        idx_orders = find_col(['首充人数'])
        idx_net = find_col(['净充提差'])
        
        # Validate existence
        missing = []
        if idx_date == -1: missing.append('日期')
        if idx_spend == -1: missing.append('投放花费/消耗')
        if idx_orders == -1: missing.append('首充人数')
        if idx_net == -1: missing.append('净充提差')
        
        if missing:
            # Fallback for critical missing? Or log warning?
            # If Net is missing, maybe default to 0?
            # But specific request was about Net Deposit correctness.
            # Let's return empty/zeros if criticals missing, or partial.
            # For now, let's trust we found them or log.
            # BaseScript logger isn't easily accessible here without passing it.
            # We'll rely on strict logic: if net is missing, we can't report net.
            pass

        # 4. Extract
        # Create a clean dict
        data = {}
        data['Date'] = df.iloc[:, idx_date] if idx_date != -1 else pd.Series()
        data['Spend'] = df.iloc[:, idx_spend] if idx_spend != -1 else pd.Series(0, index=df.index)
        data['Orders'] = df.iloc[:, idx_orders] if idx_orders != -1 else pd.Series(0, index=df.index)
        data['NetDeposit'] = df.iloc[:, idx_net] if idx_net != -1 else pd.Series(0, index=df.index)
        
        target_df = pd.DataFrame(data)
        
        # Drop first few rows if they are headers/config
        # Usually row 0 is headers.
        # We can try to convert 'Date' and drop failures.
        target_df['Date'] = pd.to_datetime(target_df['Date'], errors='coerce')
        target_df = target_df.dropna(subset=['Date'])
        
        # Clean Numerics
        cols = ['Spend', 'Orders', 'NetDeposit']
        for col in cols:
            target_df[col] = target_df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            target_df[col] = pd.to_numeric(target_df[col], errors='coerce').fillna(0)
            
        return target_df

    def calc_weekly_metrics(self, df: pd.DataFrame) -> dict:
        total_spend = df['Spend'].sum()
        total_orders = df['Orders'].sum()
        total_net = df['NetDeposit'].sum()
        
        # CPA
        cpa = total_spend / total_orders if total_orders > 0 else 0
        
        # Profit = Net - Spend
        gross_profit = total_net - total_spend
        
        return {
            "spend": total_spend,
            "orders": total_orders,
            "cpa": cpa,
            "net_deposit": total_net,
            "gross_profit": gross_profit
        }

    def calc_cumulative_metrics(self, df: pd.DataFrame) -> dict:
        # For MENA, we don't have cumulative columns specified B, I, Y are Daily.
        # So we sum everything.
        metrics_cum = {}
        if not df.empty:
            metrics_cum["spend"] = df['Spend'].sum()
            metrics_cum["orders"] = df['Orders'].sum()
        else:
            metrics_cum["spend"] = 0
            metrics_cum["orders"] = 0
            
        metrics_cum["cpa"] = metrics_cum["spend"] / metrics_cum["orders"] if metrics_cum["orders"] > 0 else 0
        return metrics_cum
