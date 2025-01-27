import os

from ...core.config import BaseConfig


class Config(BaseConfig):
    ACROSS_EMAIL_USER: str = os.environ.get("ACROSS_EMAIL_USER", "")
    ACROSS_EMAIL_PASSWORD: str = os.environ.get("ACROSS_EMAIL_PASSWORD", "")
    ACROSS_EMAIL: str = os.environ.get("ACROSS_EMAIL", "")
    ACROSS_EMAIL_HOST: str = os.environ.get("ACROSS_EMAIL_HOST", "")
    ACROSS_EMAIL_PORT: str | int = os.environ.get("ACROSS_EMAIL_PORT", 465)


email_config = Config()
