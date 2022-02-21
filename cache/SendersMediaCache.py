from typing import DefaultDict
import asyncio

from aiogram.types.input_media import InputMedia, InputMediaAudio, InputMediaPhoto, InputMediaVideo
from model.Sender import Sender
from aiogram.types import Message

from loguru import logger as log


media_types: tuple[str] = tuple(["photo", "video", "document", "audio"])
content_types: tuple[str] = tuple(["text", *media_types])
default_wait_media_time: float = 10.0


class SendersMediaCache:
    def __init__(self) -> None:
        self.cache: DefaultDict[int, dict[int, Sender]] = \
            DefaultDict(lambda : {})


    def add_media(self, message: Message) -> None:
        log.info("Adding media")
        self.cache[message.chat.id][message.from_user.id].add_media(
            self.get_media(message)
        )

    def get_media(self, message: Message) -> list[InputMedia]:
        media: list[InputMedia] = []

        if message.video is not None:
            media.append(InputMediaVideo(message.video.file_id))
        if message.photo is not None and len(message.photo) > 0:
            media.append(InputMediaPhoto(message.photo.pop().file_id))
        if message.document is not None:
            media.append(InputMediaPhoto(message.document.file_id))
        if message.audio is not None:
            media.append(InputMediaAudio(message.audio.file_id))

        return media

    def remove_sender(self, message: Message):
        chat_id: int = message.chat.id
        user_id: int = message.from_user.id

        if chat_id in self.cache:
            if user_id in self.cache[chat_id]:
                self.cache[chat_id].pop(user_id)
            if len(self.cache[chat_id]) == 0:
                self.cache.pop(chat_id)

    def is_user_waiting_media(self, message: Message) -> bool:
        return message.chat.id in self.cache \
            and message.from_user.id in self.cache[message.chat.id]

    def get_sender_media(self, message: Message) -> list[InputMedia]:
        return self.cache[message.chat.id][message.from_user.id].media

    async def wait_for_media(
        self,
        message: Message,
        time: float = default_wait_media_time
    ) -> None:

        chat_id: int = message.chat.id
        user_id: int = message.from_user.id

        self.cache[chat_id][user_id] = Sender(user_id)

        await asyncio.sleep(time)

