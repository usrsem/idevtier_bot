"""Handler for commands"""
from model.Customer import create_customer_from_message
from repository.customer_repository import save_customer
from loader import dp
from loguru import logger as log
from aiogram.types import Message


@dp.message_handler(commands=['start'])
async def send_welcome(message: Message) -> None:
    """Saves customer and sends start message"""
    customer = create_customer_from_message(message)
    log.info(customer)

    save_customer(customer)

    await message.answer(
        f"Привет, {message.from_user.first_name} !\n\n"
        "Я отлавливаю сообщения, содержащие @all и присылаю их сюда\n"
        "О проблемах пишите в чат @idevtier\n"
    )
