import typing
from pydantic import EmailStr


class EmailService:
    async def send(
        self,
        email: EmailStr,
        data: dict[typing.Any, typing.Any],
        template: str,
    ):
        raise Exception("Not yet implemented")
