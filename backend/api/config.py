from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class _Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", validate_default=False)

    database_url: str = None  # type: ignore


config = _Config()
