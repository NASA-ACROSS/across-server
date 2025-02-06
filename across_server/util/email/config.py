from ...core.config import BaseConfig


class Config(BaseConfig):
    ACROSS_EMAIL_USER: str = "nasa.across.dev@gmail.com"
    ACROSS_EMAIL_PASSWORD: str = "ask-for-password"
    ACROSS_EMAIL: str = "nasa.across.dev@gmail.com"
    ACROSS_EMAIL_HOST: str = "smtp.google.com"
    ACROSS_EMAIL_PORT: str | int = 465


email_config = Config()
