import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("POSTGRES_DB", "population_db")
    DB_HOST: str = os.getenv("POSTGRES_HOST", "db")
    DB_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))

    DATA_SOURCE: str = os.getenv("DATA_SOURCE", "wikipedia")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
