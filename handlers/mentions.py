import asyncio
from typing import Callable

from aiogram.types import Message, InputMedia, InputMediaPhoto, InputMediaDocument, \
    InputMediaVideo, InputMediaAudio
from aiogram.types.chat import Chat
from loguru import logger as log

from loader import bot, dp
from model.Customer import Customer
from model.Sender import Sender
from repository.customer_repository import get_all_cutomers

forwarding_rules: dict[str, tuple[str, ...]] = dict({
    "all": tuple(["member", "creator"]),
    "admin": tuple(["creator"])
})

_media_types = ["photo", "video", "document", "audio"]
_content_types = ["text"] + _media_types
waiting_senders: dict[int, dict[int, Sender]] = dict()


def _filter(key: str) -> Callable[[Message], bool]:
    return lambda message: key in _get_text(message)


@dp.message_handler(_filter("@all"), content_types=_content_types)
async def catch_all_tag(message: Message) -> None:
    """Catches messages with @all and sends to group users"""
    if _is_group(message):
        await _wait_for_media(message, 3)
        await _send_message_to_group_customers(message, "all")


@dp.message_handler(_filter("@admin"), content_types=_content_types)
async def catch_admin_tag(message: Message) -> None:
    """Catches messages with @all and sends to group users"""
    if _is_group(message):
        await _wait_for_media(message, 3)
        await _send_message_to_group_customers(message, "admin")


@dp.message_handler(content_types=_media_types)
async def catch_media(message: Message) -> None:
    if _is_group(message) and _is_user_waiting_media(message):
        log.info(f"catched media from {message.from_user.username}")
        waiting_senders[message.chat.id][message.from_user.id].add_media(_get_media(message))


def _is_user_waiting_media(message: Message) -> bool:
    return message.chat.id in waiting_senders and message.from_user.id in waiting_senders[message.chat.id]


def _remove_user_from_waiting_senders(message: Message):
    chat_id: int = message.chat.id
    user_id: int = message.from_user.id
    if chat_id in waiting_senders:
        if user_id in waiting_senders[chat_id]:
            waiting_senders[chat_id].pop(user_id)
        if len(waiting_senders[chat_id]) == 0:
            waiting_senders.pop(chat_id)


async def _wait_for_media(message: Message, time: float):
    chat_id: int = message.chat.id
    user_id: int = message.from_user.id
    if chat_id not in waiting_senders:
        waiting_senders[chat_id] = {user_id: Sender(user_id)}
    else:
        waiting_senders[chat_id][user_id] = Sender(user_id)
    await asyncio.sleep(time)


def _is_group(message: Message) -> bool:
    return message.chat.type in ["supergroup", "group"]


def _contains(string: str) -> Callable[[str], bool]:
    return lambda y: string in y


def _get_text(message: Message) -> str:
    text_containers: list[str] = [message.text, message.caption]
    return "\n".join([text for text in text_containers if text is not None])


def _get_media(message: Message) -> list[InputMedia]:
    media: list[InputMedia] = []
    if message.video is not None:
        media.append(InputMediaVideo(message.video.file_id))
    if message.photo is not None and len(message.photo) > 0:
        media.append(InputMediaPhoto(message.photo.pop().file_id))
    if message.document is not None:
        media.append(InputMediaDocument(message.document.file_id))
    if message.audio is not None:
        media.append(InputMediaAudio(message.audio.file_id))
    return media


async def _send_message_to_group_customers(message: Message, tag: str) -> None:
    """Sends tagged message to all users from message's group"""
    group_name: str = message.chat.title
    message_text: str = _get_text(message).replace(f"@{tag}", "").strip()
    media: list[InputMedia] = _get_media(message)
    if _is_user_waiting_media(message):
        media.extend(waiting_senders[message.chat.id][message.from_user.id].media)
        _remove_user_from_waiting_senders(message)
    is_message_contains_media: bool = len(media) > 0
    chat: Chat = await bot.get_chat(message.chat.id)
    customers: tuple[Customer] = get_all_cutomers()
    flag: bool = True

    for customer in customers:
        if flag and customer.telegram_user_id == message.from_user.id:
            flag = False
            continue

        user = await chat.get_member(customer.telegram_user_id)

        log.info("Checkig {user=} with {tag=} rules")
        if user.status in forwarding_rules[tag]:
            log.info(f"Sending message {'and media' if is_message_contains_media else ''} from group {group_name} "
                     f"to {customer.telegram_full_name}")
            await bot.send_message(
                chat_id=customer.telegram_user_id,
                text=f"@{message.from_user.username} from [{group_name}]({message.url}):\n\n"
                     f"{message_text}",
                parse_mode='markdown',
            )
            if is_message_contains_media:
                await bot.send_media_group(
                    chat_id=customer.telegram_user_id,
                    media=media
                )
