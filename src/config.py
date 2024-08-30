from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class AuthApiPrefix(BaseModel):
    prefix: str = "/auth"
    register: str = "/register"
    login_email: str = "/login-email"
    login_phone: str = "/login-phone"
    login_email_code: str = "/login-email-code"
    login_phone_code: str = "/login-phone-code"
    refresh: str = "/refresh"


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    users: str = "/users"
    auth: AuthApiPrefix = AuthApiPrefix()


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    url: PostgresDsn

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class RedisConfig(BaseModel):
    host: str
    port: int
    password: str


class AuthConfig(BaseModel):
    secret_key: str
    token_url: str = "/api/v1/auth/login"
    lifetime_seconds_access: int = 3600
    lifetime_seconds_refresh: int = 86400


class GoogleConfig(BaseModel):
    client_id: str
    client_secret: str


class EmailSenderConfig(BaseModel):
    host: str
    user: str
    password: str
    port: int


class FrontendConfig(BaseModel):
    url: str
    reset_password_path: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    redis: RedisConfig
    auth: AuthConfig
    google: GoogleConfig
    email_sender: EmailSenderConfig
    front: FrontendConfig


settings = Settings()
