from ...base_source import BaseWeeklySource
from ...mena_processor import MenaDataProcessor

class SakerwinAeSource(BaseWeeklySource):
    def __init__(self):
        super().__init__(
            sheet_id="1C3NsqkkbN-VneYqd1nLU0xQFQ1Ks2oW3KkgFoYiGS14",
            sheet_gid=1088819235, # Index 4
            app_name="SakerWin AE",
            processor=MenaDataProcessor()
        )
