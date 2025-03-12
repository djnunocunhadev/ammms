from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DB_TYPE: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # API Keys
    ACOUSTID_API_KEY: str
    MUSICBRAINZ_APP_NAME: str
    MUSICBRAINZ_VERSION: str
    DISCOGS_TOKEN: str
    BEATPORT_CLIENT_ID: str
    BEATPORT_CLIENT_SECRET: str
    LASTFM_API_KEY: str
    LASTFM_API_SECRET: str

    # Application
    APP_NAME: str
    APP_ENV: str
    DEBUG: bool
    SECRET_KEY: str
    API_PREFIX: str
    CORS_ORIGINS: List[str]

    # File Storage
    UPLOAD_DIR: str
    TEMP_DIR: str
    MAX_UPLOAD_SIZE: int

    # Processing
    AUDIO_FORMATS: List[str]
    ENABLE_NEURAL_PROCESSING: bool
    BATCH_SIZE: int
    NUM_WORKERS: int

    # Cache
    CACHE_TTL: int
    METADATA_CACHE_TTL: int

    # Logging
    LOG_LEVEL: str
    LOG_FILE: str

    class Config:
        env_file = ".env"

settings = Settings()
