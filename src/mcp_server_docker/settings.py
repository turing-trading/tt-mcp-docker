from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings, cli_parse_args=True):
    model_config = SettingsConfigDict(
        env_prefix="mcp_server_", env_nested_delimiter="__"
    )

    docker_secrets: dict[str, SecretStr] = {}
