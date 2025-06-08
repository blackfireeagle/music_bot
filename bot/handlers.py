import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Dict
from services import get_genius
from storage import storage
from keyboards import (
    get_main_keyboard,
    get_language_keyboard,
    get_song_actions_keyboard
)
import json
import os


# Инициализация логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log'
)
logger = logging.getLogger(__name__)

# Инициализация роутера
router = Router()
genius = get_genius()
admin_router = Router()

os.makedirs(os.path.join(os.path.dirname(__file__), "locales"), exist_ok=True)

# Загрузка локализаций
def load_locales() -> Dict[str, Dict[str, str]]:
    locales = {
        "ru": {
            "start": "Привет! Я музыкальный бот.",
            "help": "Доступные команды:\n\n🎵 Найти песню\n⭐ Избранное\n🌍 Язык\nℹ️ О проекте",
            "search_song": "Введите название песни:",
            "song_found": "Найдена песня: {title} - {artist}",
            "no_favorites": "У вас пока нет избранного.",
            "favorites": "Ваше избранное:\n\n🎵 Песни:\n{songs}",
            "language_changed": "Язык изменен на русский.",
            "error": "Ошибка, попробуйте позже.",
            "added_to_favorites": "Добавлено в избранное!",
            "lyrics": "Текст песни {title}:\n\n{lyrics}",
            "choose_option": "Выберите действие:",
            "no_results": "По вашему запросу ничего не найдено.",
            "about": "Это музыкальный бот, который помогает находить тексты песен с помощью Genius API."
        },
        "en": {
            "start": "Hello! I'm a music bot.",
            "help": "Available commands:\n\n🎵 Find song\n⭐ Favorites\n🌍 Language\nℹ️ About",
            "search_song": "Enter song title:",
            "song_found": "Found song: {title} - {artist}",
            "no_favorites": "You don't have favorites yet.",
            "favorites": "Your favorites:\n\n🎵 Songs:\n{songs}",
            "language_changed": "Language changed to English.",
            "error": "Error, please try again.",
            "added_to_favorites": "Added to favorites!",
            "lyrics": "Lyrics for {title}:\n\n{lyrics}",
            "choose_option": "Choose an option:",
            "no_results": "No results found for your query.",
            "about": "This is a music bot that helps you find song lyrics using Genius API."
        }
    }

    locales_dir = os.path.join(os.path.dirname(__file__), "locales")
    os.makedirs(locales_dir, exist_ok=True)

    for lang, translations in locales.items():
        with open(os.path.join(locales_dir, f"{lang}.json"), "w", encoding="utf-8") as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)

    return locales

# Инициализация локализаций
locales = load_locales()


class SearchStates(StatesGroup):
    waiting_for_song = State()


def get_translation(user_id: int, key: str) -> str:

    """Получение перевода по ключу для языка пользователя"""

    user = storage.get_user(user_id)
    lang = user["language"]
    return locales.get(lang, {}).get(key, key)


async def show_main_menu(user_id: int, message: Message):

    """Показывает главное меню"""

    lang = storage.get_user(user_id)["language"]
    await message.answer(
        text=get_translation(user_id, "choose_option"),  # Добавьте этот перевод в locales
        reply_markup=get_main_keyboard(lang)
    )


@router.message(Command("start"))
async def cmd_start(message: Message):

    """Обработчик команды /start"""

    user_id = message.from_user.id
    try:
        await message.answer(
            text=get_translation(user_id, "start"),
            reply_markup=get_main_keyboard(storage.get_user(user_id)["language"])
        )
    except Exception as e:
        logger.error(f"Error in /start: {e}")
        await message.answer(get_translation(user_id, "start"))

@router.message(Command("help"))
async def cmd_help(message: Message):

    """Обработчик команды /help"""

    user_id = message.from_user.id
    help_text = get_translation(user_id, "help")
    await message.answer(help_text)


@router.message(F.text.in_(["🎵 Найти песню", "🎵 Find song"]))
async def search_song_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(SearchStates.waiting_for_song)
    await message.answer(get_translation(user_id, "search_song"))


@router.message(SearchStates.waiting_for_song)
async def search_song_result(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = storage.get_user(user_id)["language"]

    try:
        songs = await genius.search_songs(message.text)
        if not songs:
            await message.answer(get_translation(user_id, "error"))
            return

        for song in songs[:5]:
            title = song["title"]
            artist = song["primary_artist"]["name"]
            text = get_translation(user_id, "song_found").format(title=title, artist=artist)
            await message.answer(
                text,
                reply_markup=get_song_actions_keyboard(song["id"], lang)
            )
    except Exception as e:
        logger.error(f"Error searching songs: {e}")
        await message.answer(get_translation(user_id, "error"))
    finally:
        await state.clear()


@router.message(F.text.in_(["ℹ️ О проекте", "ℹ️ About"]))
async def show_about(message: Message):
    user_id = message.from_user.id
    await message.answer(get_translation(user_id, "about"))


@router.message(F.text.in_(["⭐ Избранное", "⭐ Favorites"]))
async def show_favorites(message: Message):
    user_id = message.from_user.id
    favorites = storage.get_favorites(user_id)

    if not favorites["songs"]:
        await message.answer(get_translation(user_id, "no_favorites"))
    else:
        songs_text = "\n".join([f"- {s['title']} by {s['primary_artist']['name']}" for s in favorites["songs"]]) or "None"
        text = get_translation(user_id, "favorites").format(songs=songs_text)
        await message.answer(text)


@router.message(F.text.in_(["🌍 Язык", "🌍 Language"]))
async def change_language(message: Message):
    user_id = message.from_user.id
    await message.answer(
        get_translation(user_id, "language_changed"),
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    storage.set_language(user_id, lang)
    await callback.answer(get_translation(user_id, "language_changed"))
    await show_main_menu(user_id, callback.message)


@router.callback_query(F.data.startswith("lyrics_"))
async def show_lyrics(callback: CallbackQuery):
    user_id = callback.from_user.id
    song_id = int(callback.data.split("_")[1])

    try:
        data = await genius._make_request(f"/songs/{song_id}")
        song = data["response"]["song"]
        lyrics_url = song["url"]
        title = song["title"]

        text = get_translation(user_id, "lyrics").format(
            title=title,
            lyrics=f"Ссылка на текст песни: {lyrics_url}"
        )
        await callback.message.answer(text)
    except Exception as e:
        logger.error(f"Error getting lyrics: {e}")
        await callback.answer(get_translation(user_id, "error"))


@router.callback_query(F.data.startswith("fav_song_"))
async def add_song_to_favorites(callback: CallbackQuery):
    user_id = callback.from_user.id
    song_id = int(callback.data.split("_")[2])

    try:
        data = await genius._make_request(f"/songs/{song_id}")
        song = data["response"]["song"]

        storage.add_favorite_song(user_id, {
            "id": song["id"],
            "title": song["title"],
            "primary_artist": {
                "name": song["primary_artist"]["name"],
                "id": song["primary_artist"]["id"]
            }
        })

        await callback.answer(get_translation(user_id, "added_to_favorites"))
    except Exception as e:
        logger.error(f"Error adding song to favorites: {e}")
        await callback.answer(get_translation(user_id, "error"))


@admin_router.message(Command("stats"))
async def cmd_stats(message: Message):

    """Статистика бота"""

    total_users = len(storage.data)
    active_today = 1

    await message.answer(
        f"📊 Статистика:\n"
        f"• Пользователей: {total_users}\n"
        f"• Активных сегодня: {active_today}"
    )


@admin_router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):

    """Рассылка фиксированного сообщения"""

    text = (
        "Привет! Будем что-то искать?\n"
        "Hello! Are we going to find something new?"
    )

    for user_id in storage.data:
        if user_id != "banned":
            try:
                await message.bot.send_message(user_id, f"📢 Рассылка:\n{text}")
            except Exception as e:
                logger.error(f"Ошибка отправки для {user_id}: {e}")

    await message.answer(f"✅ Рассылка завершена (отправлено {len(storage.data)} пользователям)")


@admin_router.message(F.text.startswith("/ban "))
async def cmd_ban(message: Message):
    user_id = int(message.text.split()[1])
    # Здесь логика бана (добавьте в storage.py)
    await message.answer(f"⛔ Пользователь {user_id} заблокирован")