import asyncpg

from app.utils import secrets


class AppContext:
    def __init__(self, *, secrets_dir: str):
        self.secrets: secrets.SecretsReader = secrets.SecretsReader(
            secrets_dir
        )

    async def on_startup(self, app=None):
        self.db = await asyncpg.create_pool(dsn='postgresql://postgres:postgres123@postgres:5432/MyLittleYandexDisk')

    async def on_shutdown(self, app=None):
        if self.db:
            await self.db.close()
