from aiogram.types import InputMedia


class Sender:
    def __init__(self, user_id: int):
        self.media: list[InputMedia] = []
        self.user_id: int = user_id

    def add_media(self, media: list[InputMedia]):
        self.media.extend(media)