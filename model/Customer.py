from aiogram import types
from typing import NamedTuple


class Customer(NamedTuple):
    """Base customer model"""
    telegram_user_id: int
    telegram_username: str
    telegram_full_name: str


def create_customer_from_message(message: types.Message) -> Customer:
    return Customer(
        telegram_user_id=message.from_user.id,
        telegram_username=message.from_user.username,
        telegram_full_name=message.from_user.full_name
    )
