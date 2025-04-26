from typing import Annotated
from dotenv import find_dotenv
from pydantic import (
    BeforeValidator,
    HttpUrl,
    SecretStr,
    TypeAdapter,
)
from pydantic import (
    BeforeValidator,
    SecretStr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

def check_str_is_http(x: str) -> str:
    http_url_adapter = TypeAdapter(HttpUrl)
    return str(http_url_adapter.validate_python(x))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        validate_default=False,
    )
    MODE: str | None = None

    AUTH_SECRET: SecretStr | None = None

    OPENAI_API_KEY: SecretStr | None = None
    GOOGLE_API_KEY: SecretStr | None = None

    FIRECRAWL_API_KEY: str | None = None
    TEXT_MODEL: str | None = None
    VISION_MODEL: str | None = None
    EMBEDDINGS_MODEL: str | None = None

    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "default"
    LANGCHAIN_ENDPOINT: Annotated[str, BeforeValidator(check_str_is_http)] = (
        "https://api.smith.langchain.com"
    )
    LANGCHAIN_API_KEY: SecretStr | None = None

    ELASTIC_SEARCH_URL: str | None = None
    ELASTIC_SEARCH_API: str | None = None

settings = Settings()
