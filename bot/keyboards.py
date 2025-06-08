from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_keyboard(lang: str = 'ru') -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    if lang == 'ru':
        buttons = [
            KeyboardButton(text="🎵 Найти песню"),
            KeyboardButton(text="⭐ Избранное"),
            KeyboardButton(text="🌍 Язык"),
            KeyboardButton(text="ℹ️ О проекте")
        ]
    else:
        buttons = [
            KeyboardButton(text="🎵 Find song"),
            KeyboardButton(text="⭐ Favorites"),
            KeyboardButton(text="🌍 Language"),
            KeyboardButton(text="ℹ️ About")
        ]

    for button in buttons:
        builder.add(button)

    return builder.adjust(2).as_markup(resize_keyboard=True)


def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
    )
    return builder.as_markup()


def get_song_actions_keyboard(song_id: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if lang == 'ru':
        builder.add(
            InlineKeyboardButton(text="📝 Текст песни", callback_data=f"lyrics_{song_id}"),
            InlineKeyboardButton(text="⭐ В избранное", callback_data=f"fav_song_{song_id}")
        )
    else:
        builder.add(
            InlineKeyboardButton(text="📝 Lyrics", callback_data=f"lyrics_{song_id}"),
            InlineKeyboardButton(text="⭐ Add to favorites", callback_data=f"fav_song_{song_id}")
        )

    return builder.as_markup()


def get_artist_actions_keyboard(artist_id: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if lang == 'ru':
        builder.add(
            InlineKeyboardButton(text="🎵 Популярные песни", callback_data=f"songs_{artist_id}"),
            InlineKeyboardButton(text="⭐ В избранное", callback_data=f"fav_artist_{artist_id}")
        )
    else:
        builder.add(
            InlineKeyboardButton(text="🎵 Popular songs", callback_data=f"songs_{artist_id}"),
            InlineKeyboardButton(text="⭐ Add to favorites", callback_data=f"fav_artist_{artist_id}")
        )

    return builder.as_markup()