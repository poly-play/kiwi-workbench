from ..base_source import BaseWeeklySource

class JeetupSource(BaseWeeklySource):
    def __init__(self):
        super().__init__(
            sheet_id="1K1xMyNLGyfqxt2VE3BAliKD3QQLBmVnttk2WOXoAYAY",
            app_name="Jeetup"
        )
