from pydantic_settings import BaseSettings, SettingsConfigDict

from functools import cached_property

class Settings(BaseSettings):
    openai_api_key: str
    mongodb_uri: str
    redis_host: str
    redis_port: int
    redis_user: str
    redis_pass: str
    debug_mode: bool = False
    jwt_algorithm: str
    jwt_private_key_path: str
    jwt_public_key_path: str
    tavily_api_key: str
    mem0_api_key: str
    qdrant_url: str
    qdrant_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @cached_property
    def private_key(self) -> str:
        with open(self.jwt_private_key_path, "r") as f:
            return f.read()

    @cached_property
    def public_key(self) -> str:
        with open(self.jwt_public_key_path, "r") as f:
            return f.read()

settings = Settings()
