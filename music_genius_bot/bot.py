import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from config import config
from handlers import router, admin_router


# Классы middleware
class LoggingMiddleware:
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        logging.info(f"User {event.from_user.id} sent: {event.text}")
        return await handler(event, data)


class AdminMiddleware:
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if event.from_user.id not in config.ADMIN_IDS:
            await event.answer("🚫 Доступ запрещён!")
            return
        return await handler(event, data)


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

async def main():
    logger = logging.getLogger(__name__)
    try:
        logger.info("Запуск бота...")
        bot = Bot(token=config.BOT_TOKEN)
        dp = Dispatcher()

        # Регистрация middleware
        dp.message.middleware.register(LoggingMiddleware())
        dp.message.middleware.register(AdminMiddleware())
        dp.callback_query.middleware.register(AdminMiddleware())

        dp.include_router(admin_router)
        dp.include_router(router)

        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот начал поллинг...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
    finally:
        if 'bot' in locals():
            await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())