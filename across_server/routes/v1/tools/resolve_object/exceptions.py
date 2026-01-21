from fastapi import status

from .....core.exceptions import AcrossHTTPException


class NameNotFoundException(AcrossHTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Could not resolve name {name} into coordinates.",
            log_data={"entity": "Name Resolver", "name": name},
        )
