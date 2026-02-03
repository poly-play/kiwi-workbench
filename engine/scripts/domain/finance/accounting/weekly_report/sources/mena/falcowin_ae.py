from ...base_source import BaseWeeklySource
from ...mena_processor import MenaDataProcessor

class FalcowinAeSource(BaseWeeklySource):
    def __init__(self):
        super().__init__(
            sheet_id="1C3NsqkkbN-VneYqd1nLU0xQFQ1Ks2oW3KkgFoYiGS14",
            sheet_gid=1342066374, # Index 2
            app_name="Falcowin AE",
            processor=MenaDataProcessor()
        )
