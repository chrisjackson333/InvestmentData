"""Signal engine domain configuration: strategy params (SIGNAL_) and
database connection (DB_) as two separate settings classes.
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SignalEngineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIGNAL_")

    sma_period: int = 20


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = "localhost"
    port: int = 5432
    name: str = "investment_platform"
    user: str = "investment_platform"
    password: SecretStr = SecretStr("investment_platform")

    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )
