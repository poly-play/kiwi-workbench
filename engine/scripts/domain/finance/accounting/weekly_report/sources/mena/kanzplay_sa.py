from ...base_source import BaseWeeklySource
from ...mena_processor import MenaDataProcessor

class KanzplaySaSource(BaseWeeklySource):
    def __init__(self):
        super().__init__(
            sheet_id="1C3NsqkkbN-VneYqd1nLU0xQFQ1Ks2oW3KkgFoYiGS14",
            sheet_gid=0, # First Sheet
            app_name="Kanzplay SA",
            processor=MenaDataProcessor()
        )
