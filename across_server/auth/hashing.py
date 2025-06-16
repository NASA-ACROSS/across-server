from argon2 import PasswordHasher

password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=64,
    salt_len=64,
    encoding="utf-8",
)
