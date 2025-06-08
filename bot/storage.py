import json
import os
from typing import Dict, List, Optional


class Storage:

    """Класс для хранения данных пользователей"""

    def __init__(self, filename: str = "user_data.json"):
        self.filename = filename
        self.data: Dict[int, Dict] = self._load_data()

    def _load_data(self) -> Dict[int, Dict]:

        """Загрузка данных из файла"""

        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_data(self):

        """Сохранение данных в файл"""

        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_user(self, user_id: int) -> Dict:

        """Получение данных пользователя"""

        if user_id not in self.data:
            self.data[user_id] = {
                "language": "ru",
                "favorite_songs": [],
                "favorite_artists": []
            }
        return self.data[user_id]

    def set_language(self, user_id: int, language: str):

        """Установка языка пользователя"""

        user = self.get_user(user_id)
        user["language"] = language
        self._save_data()

    def add_favorite_song(self, user_id: int, song: Dict):

        """Добавление песни в избранное"""

        user = self.get_user(user_id)
        if not any(s["id"] == song["id"] for s in user["favorite_songs"]):
            user["favorite_songs"].append(song)
            self._save_data()
            return True
        return False

    def add_favorite_artist(self, user_id: int, artist: Dict):

        """Добавление исполнителя в избранное"""

        user = self.get_user(user_id)
        if artist["id"] not in [a["id"] for a in user["favorite_artists"]]:
            user["favorite_artists"].append(artist)
            self._save_data()

    def remove_favorite_song(self, user_id: int, song_id: int):

        """Удаление песни из избранного"""

        user = self.get_user(user_id)
        user["favorite_songs"] = [s for s in user["favorite_songs"] if s["id"] != song_id]
        self._save_data()

    def remove_favorite_artist(self, user_id: int, artist_id: int):

        """Удаление исполнителя из избранного"""

        user = self.get_user(user_id)
        user["favorite_artists"] = [a for a in user["favorite_artists"] if a["id"] != artist_id]
        self._save_data()

    def get_favorites(self, user_id: int) -> Dict[str, List]:

        """Получение избранного пользователя"""

        user = self.get_user(user_id)
        return {
            "songs": user["favorite_songs"],
            "artists": user["favorite_artists"]
        }

    def ban_user(self, user_id: int):

        """Добавить пользователя в чёрный список"""

        if "banned" not in self.data:
            self.data["banned"] = []
        if user_id not in self.data["banned"]:
            self.data["banned"].append(user_id)
            self._save_data()

    def unban_user(self, user_id: int):

        """Разбанить пользователя"""

        if "banned" in self.data:
            self.data["banned"] = [id for id in self.data["banned"] if id != user_id]
            self._save_data()

# Инициализация хранилища
storage = Storage()
