from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    GRPQ_API_KEY: str
    GOOGLE_API_KEY: str
    QDRANT_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )