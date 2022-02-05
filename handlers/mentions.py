from loader import bot, dp
from model.Customer import Customer
from repository.customer_repository import get_all_cutomers
from aiogram.types.chat import Chat
from aiogram.types import Message
from loguru import logger as log


forwarding_rules: dict[str, tuple[str, ...]] = dict({
    "all": tuple(["member", "creator"]),
    "admin": tuple(["creator"])
})


@dp.message_handler(lambda message: "@all" in message.text)
async def catch_all_tag(message: Message) -> None:
    """Catches messages with @all and sends to group users"""
    if _is_group(message):
        await _send_message_to_group_customers(message, "all")


@dp.message_handler(lambda message: "@admin" in message.text)
async def catch_admin_tag(message: Message) -> None:
    """Catches messages with @all and sends to group users"""
    if _is_group(message):
        await _send_message_to_group_customers(message, "admin")


def _is_group(message: Message) -> bool:
    return message.chat.type in ["supergroup", "group"]


async def _send_message_to_group_customers(message: Message, tag: str) -> None:
    """Sends tagged message to all users from message's group"""
    group_name: str = message.chat.title
    message_text: str = message.text.replace(f"@{tag}", "").strip()
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
            log.info(f"Sending message from group {group_name} "
                     f"to {customer.telegram_full_name}")
            await bot.send_message(
                chat_id=customer.telegram_user_id,
                text=f"From group: {group_name}\n\n"
                    f"{message_text}\n"
                    f"{message.url}",
            )
