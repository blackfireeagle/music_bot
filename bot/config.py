import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv('BOT_TOKEN')
    GENIUS_TOKEN: str = os.getenv('GENIUS_TOKEN')
    ADMIN_IDS: list[int] = [int(id) for id in os.getenv('ADMIN_IDS').split(',')] if os.getenv('ADMIN_IDS') else []

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("Не указан BOT_TOKEN в .env файле")
        if not cls.GENIUS_TOKEN:
            raise ValueError("Не указан GENIUS_TOKEN в .env файле")
        if not cls.ADMIN_IDS:
            logging.warning("Не указаны ADMIN_IDS в .env файле")

config = Config()
config.validate()