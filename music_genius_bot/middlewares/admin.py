from config import config
import logging


class AdminMiddleware:
    async def __call__(self, handler, event, data):
        if not config.ADMIN_IDS:
            logging.error("Список ADMIN_IDS пуст! Проверьте .env")
            return await handler(event, data)

        if event.from_user.id not in config.ADMIN_IDS:
            await event.answer("🔒 Доступ запрещён!")
            return
        return await handler(event, data)