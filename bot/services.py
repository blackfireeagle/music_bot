import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from config import config
import logging
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log'
)
logger = logging.getLogger(__name__)

class GeniusAPI:
    BASE_URL = "https://api.genius.com"

    def __init__(self):
        self.token = config.GENIUS_TOKEN
        self.session = None
        self.cache: Dict[str, Any] = {}


    async def initialize(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            )

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None


    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        if not self.session or self.session.closed:
            await self.initialize()

        url = f"{self.BASE_URL}{endpoint}"
        if params != None:
            url += "?"
            for key, value in params.items():
                url += f"{key}={value}&"
            url = url[:-1]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

        try:
            async with self.session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=ssl_context
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Ошибка API: {response.status} | {error_text}")
                    raise Exception(f"API Error: {response.status}")

                return await response.json()

        except asyncio.TimeoutError:
            logger.error("Таймаут запроса к Genius API")
            raise Exception("Сервер не ответил вовремя")
        except Exception as e:
            logger.error(f"Ошибка в _make_request: {e}", exc_info=True)
            raise Exception(f"Ошибка API: {e}")


    async def search_songs(self, query: str) -> list:
        """Поиск песен по запросу"""
        try:
            response = await self._make_request("/search", params={"q": query})
            return response["response"]["hits"]
        except Exception as e:
            logging.error(f"Error searching songs: {e}")
            return []

    async def get_song_lyrics(self, song_id: int) -> Optional[str]:
        try:
            data = await self._make_request(f"/songs/{song_id}")
            song = data["response"]["song"]
            return f"Текст песни {song['title']}:\n\nURL: {song['url']}\n\nПримечание: Для получения полного текста посетите страницу песни на Genius."
        except Exception as e:
            logger.error(f"Error getting song lyrics: {e}")
            return None

    async def get_new_releases(self, limit: int = 10) -> List[Dict]:
        try:
            data = await self._make_request(
                "/albums/new",
                params={"per_page": limit}
            )
            return data["response"]["albums"]
        except Exception as e:
            logger.error(f"Error getting new releases: {e}")
            return []

def get_genius() -> GeniusAPI:
    return GeniusAPI()