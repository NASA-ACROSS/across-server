import hashlib

from .config import auth_config


def hash_secret_key(
    key: str,
    salt: str,
) -> str:
    pepper = auth_config.SERVICE_ACCOUNT_SECRET_KEY
    key_salt_pepper = key + salt + pepper

    return hashlib.sha512(key_salt_pepper.encode()).hexdigest()
