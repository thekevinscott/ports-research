from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """GENERATE_EMBEDDING_-prefixed environment configuration.

    No module-level instance: base_url has no default, since a local llama.cpp
    server, OpenRouter, and a hosted embeddings provider all live at different
    URLs and defaulting to any one of them would silently pick a provider the
    caller never chose. Instantiating eagerly at import time would make every
    import of this package fail without the env var set; callers build
    `Settings()` themselves once they actually need it.
    """

    model_config = SettingsConfigDict(env_prefix="GENERATE_EMBEDDING_")

    base_url: str
    api_key: SecretStr | None = None
