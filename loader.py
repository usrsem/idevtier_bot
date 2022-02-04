"""Telegram bot for @all mentions in groups"""
from aiogram import Bot, Dispatcher
from config.bot_consts import API_TOKEN


bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
