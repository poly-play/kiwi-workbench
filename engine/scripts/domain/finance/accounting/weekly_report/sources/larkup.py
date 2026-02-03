from ..base_source import BaseWeeklySource

class LarkupSource(BaseWeeklySource):
    def __init__(self):
        super().__init__(
            sheet_id="1393dcndMJsxmuI5HDoicAQJKFIv-irbKkXg0VGXBTw0",
            app_name="Larkup"
        )
