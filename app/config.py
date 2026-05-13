from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    AUTH0_NAMESPACE: str
    MONGO_URI: str
    MONGO_DB_NAME: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
