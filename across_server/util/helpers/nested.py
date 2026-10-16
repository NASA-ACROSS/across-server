from typing import Any

from pydantic import BaseModel


def has_key(obj: dict, path: str):
    keys = path.split(".")
    current = obj

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    return True


def get_value(model: BaseModel | dict, path: str) -> Any:
    keys = path.split(".")
    current = model

    for key in keys:
        if isinstance(current, BaseModel) and hasattr(current, key):
            next = getattr(current, key)
            current = next
        elif isinstance(current, dict) and key in current:
            current = current[key]
        else:
            current = None

    return current
