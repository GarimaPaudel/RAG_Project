from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    QDRANT_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

settings = Settings()