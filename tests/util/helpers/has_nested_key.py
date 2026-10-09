from typing import Any

from pydantic import BaseModel


def has_nested_key(obj: dict, path: str):
    keys = path.split(".")
    current = obj

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    return True


def get_nested_data(model: BaseModel, path: str) -> Any:
    keys = path.split(".")
    current = model

    for key in keys:
        next = getattr(current, key)

        if isinstance(next, BaseModel):
            current = next
        else:
            current = next

    return current
