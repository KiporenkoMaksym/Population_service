import asyncpg
from src.config import settings

class DatabaseManager:
    def __init__(self):
        self.dsn = settings.database_url

    async def create_tables(self):
        conn = await asyncpg.connect(self.dsn)
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS country_population (
                    id SERIAL PRIMARY KEY,
                    country VARCHAR(255) NOT NULL,
                    region VARCHAR(255) NOT NULL,
                    population BIGINT NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    UNIQUE(country, source)
                );
            """)
        finally:
            await conn.close()

    async def get_connection(self):
        return await asyncpg.connect(self.dsn)
