import yaml
import pandas as pd
import sys
from pathlib import Path

# Fix path for standalone execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from engine.scripts.core.base_script import BaseScript

class GenericReporter(BaseScript):
    DOMAIN = "tech" # Default, but overridable by config
    SUB_DOMAIN = "data"
    JOB_NAME = "generic_reporter"
    
    def add_arguments(self, parser):
        parser.add_argument("--config", required=True, help="Path to Report Config YAML")
        parser.add_argument("--period", default="yesterday", 
                          choices=["today", "yesterday", "this_week", "last_week", "this_month", "last_month"],
                          help="Time period for the report")

    def run(self):
        # 1. Load Report Config
        with open(self.args.config, 'r', encoding='utf-8') as f:
            report_cfg = yaml.safe_load(f)

        # Allow Domain Overrides
        self.DOMAIN = report_cfg.get('domain', self.DOMAIN)
        self.SUB_DOMAIN = report_cfg.get('sub_domain', self.SUB_DOMAIN)
        
        # Output Manager setup
        specific_job = report_cfg.get('job_name', self.JOB_NAME)
        from engine.scripts.utils.output_manager import OutputManager
        self.out = OutputManager(
            domain=self.DOMAIN,
            sub_domain=self.SUB_DOMAIN,
            job_name=f"{specific_job}_{self.args.env}",
            app_name=self.args.app,
            config=self.config
        )
        
        # 2. Connector
        source_name = report_cfg.get('source', 'warehouse') 
        db = self.get_connector(source_name)
        
        # 3. Date Logic
        import datetime
        from dateutil.relativedelta import relativedelta # Ensure python-dateutil is available, else use simple timedelta
        
        now = datetime.datetime.now()
        today_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        period = self.args.period
        start_time = today_date
        end_time = today_date + datetime.timedelta(days=1)
        
        if period == "today":
            start_time = today_date
            end_time = today_date + datetime.timedelta(days=1)
        
        elif period == "yesterday":
            start_time = today_date - datetime.timedelta(days=1)
            end_time = today_date
            
        elif period == "this_week":
            # Assuming Monday is start
            start_time = today_date - datetime.timedelta(days=today_date.weekday())
            end_time = today_date + datetime.timedelta(days=1)
            
        elif period == "last_week":
            this_monday = today_date - datetime.timedelta(days=today_date.weekday())
            start_time = this_monday - datetime.timedelta(weeks=1)
            end_time = this_monday
            
        elif period == "this_month":
            start_time = today_date.replace(day=1)
            end_time = (start_time + relativedelta(months=1))
            
        elif period == "last_month":
            this_month_start = today_date.replace(day=1)
            start_time = (this_month_start - relativedelta(months=1))
            end_time = this_month_start

        # Context functionality
        # Prefer app_id from config (int), fallback to CLI arg (str), then default
        app_id = self.config.get('datasources', {}).get('app_id') or self.config.get('app_id') or self.args.app or "1004"
        
        context_vars = {
            "app_id": app_id, 
            "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "period": period,
            "today": today_date.strftime('%Y-%m-%d'),
            "now": now.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # SQL Injection
        sql_query = report_cfg.get('sql')
        if not sql_query:
            # Maybe it's a file path?
            sql_path = report_cfg.get('sql_file')
            if sql_path:
                with open(sql_path, 'r') as f:
                    sql_query = f.read()
            else:
                 raise ValueError("Report Config must provide 'sql' or 'sql_file'")
                 
        try:
            for k, v in context_vars.items():
                sql_query = sql_query.replace(f"{{{{{k}}}}}", str(v)) 
        except Exception as e:
            print(f"[Warn] SQL Substitution failed: {e}")

        print(f"Executing SQL on {source_name}...")
        print(f"[Report] Period: {period} | Range: {context_vars['start_time']} -> {context_vars['end_time']}")
        
        df = db.query(sql_query)
        
        # 4. Check Condition
        condition = report_cfg.get('trigger_rule', 'len(df) > 0') 
        is_triggered = eval(condition, {"df": df, "pd": pd})
        
        meta = {
            "result_count": len(df),
            "triggered": is_triggered,
            "period": period
        }
        
        if is_triggered:
            # 5. Export
            csv_name = f"{period}_report.csv"
            csv_path = self.out.get_path(csv_name)
            df.to_csv(csv_path, index=False)
            
            # 6. Notify
            msg_tmpl = report_cfg.get('message', "Report Triggered: {count} rows.")
            # Inject context into message template too
            full_context = {**context_vars, "count": len(df), "df": df}
            try:
                msg = msg_tmpl.format(**full_context)
            except:
                msg = msg_tmpl # Fallback
            
            self.notifier.send(
                title=f"📊 {report_cfg.get('title', 'Generic Report')}",
                message=f"{msg}\n\nDownload: {csv_path}",
                key=f"{self.DOMAIN}.{self.SUB_DOMAIN}"
            )
            self.NOTIFY_ON_SUCCESS = False
            
        else:
            print("Condition not met. No alert sent.")
            self.NOTIFY_ON_SUCCESS = False 
            
        return meta

if __name__ == "__main__":
    GenericReporter().execute()
