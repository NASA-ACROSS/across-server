from argon2 import PasswordHasher

from .config import auth_config

password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=64,
    salt_len=64,
    encoding="utf-8",
)


def hash_secret_key(
    key: str,
) -> str:
    pepper = auth_config.SERVICE_ACCOUNT_SECRET_KEY
    key_pepper = key + pepper

    return password_hasher.hash(key_pepper)
