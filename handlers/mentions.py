from typing import Callable

from aiogram.types import Message, InputMedia
from aiogram.types.chat import Chat
from loguru import logger as log

from loader import bot, dp
from model.Customer import Customer
from repository.customer_repository import get_all_cutomers
from cache.SendersMediaCache import SendersMediaCache, content_types, media_types

forwarding_rules: dict[str, tuple[str, ...]] = dict({
    "all": tuple(["member", "creator", "administrator"]),
    "admin": tuple(["creator", "administrator"])
})

tags: set[str] = {"@all", "@admin"}
media_cache: SendersMediaCache = SendersMediaCache()


def group_catcher() -> Callable[[Message], bool]:
    return lambda message: _in_group(message)

def _waiting_media_catcher() -> Callable[[Message], bool]:
    return lambda m : _in_group(m) and media_cache.is_user_waiting_media(m)


@dp.message_handler(_waiting_media_catcher(), content_types=media_types)
async def catch_and_save_media(message: Message) -> None:
    """Catches media if already was tagged @all or @admin"""
    log.info(f"Catched media from {message.from_user.username}")
    media_cache.add_media(message)


@dp.message_handler(group_catcher(), content_types=content_types)
async def catch_all_tag(message: Message) -> None:
    """
    Catches messages from groups with @all or @admin,
    waits and sends to group users
    """
    log.info("haha")
    tag: str = _get_tag(message)
    if tag:
        log.info(f"Catched message with {tag}")
        await media_cache.wait_for_media(message)
        await _send_message_to_group_customers(message, tag[1:])


async def _send_message_to_group_customers(message: Message, tag: str) -> None:
    """Sends tagged message to all users from message's group"""
    group_name: str = message.chat.title
    message_text: str = _get_text(message).replace(f"@{tag}", "").strip()
    media: list[InputMedia] = _get_media_for_sending(message)

    for customer in await _get_customers_for_sending(message, tag):
        log.info(f"Sending message "
                 f"{'and media' if media else ''} "
                 f"from group {group_name} "
                 f"to {customer.telegram_full_name}"
        )

        await bot.send_message(
            chat_id=customer.telegram_user_id,
            text=f"{get_username(message)} "
                 f"from [{group_name}]({message.url}):\n\n"
                 f"{message_text}",
            parse_mode='markdown',
        )

        if media:
            await bot.send_media_group(
                chat_id=customer.telegram_user_id,
                media=media,
                disable_notification=True
            )


def _get_media_for_sending(message: Message) -> list[InputMedia]:
    media: list[InputMedia] = media_cache.get_media(message)

    if media_cache.is_user_waiting_media(message):
        media.extend(media_cache.get_sender_media(message))
        media_cache.remove_sender(message)

    return media


async def _get_customers_for_sending(
    message: Message,
    tag: str
) -> list[Customer]:

    chat: Chat = await bot.get_chat(message.chat.id)
    all_customers: tuple[Customer] = get_all_cutomers()
    result_customers: list[Customer] = []

    flag: bool = True
    for customer in all_customers:
        if flag and customer.telegram_user_id == message.from_user.id:
            flag = False
            continue

        user = await chat.get_member(customer.telegram_user_id)
        log.info(f"Checkig {user=} with {tag=} rules")
        if user.status in forwarding_rules[tag]:
            result_customers.append(customer)

    return result_customers


def get_username(message: Message) -> str:
    if message.from_user.username is not None:
        return "@" + message.from_user.username
    return message.from_user.full_name


def _get_tag(message: Message) -> str:
    for tag in tags:
        if tag in _get_text(message):
            return tag
    return ""


def _get_text(message: Message) -> str:
    text_containers: tuple[str, str] = tuple((message.text, message.caption))
    return "\n".join([t for t in text_containers if t is not None])

def _in_group(message: Message) -> bool:
    return message.chat.type in {"supergroup", "group"}
