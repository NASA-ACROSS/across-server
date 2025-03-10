from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Generic, TypeVar

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# string of UUID or email
S = TypeVar("S", str, EmailStr)

D = TypeVar("D")


# Base Token Data class to be extended by specific token payloads
class TokenData(BaseModel, Generic[S]):
    model_config = ConfigDict(extra="ignore")

    sub: S
    # Common expiration field for all tokens.
    exp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=15)
    )


# Type variable for Pydantic models
T = TypeVar("T", bound=TokenData)
# Generic type var for data that will be encoded to T
U = TypeVar("U")


# Abstract Base Token class
class Token(ABC, Generic[T, U]):
    key: str  # The secret key used for encoding/decoding

    @property
    @abstractmethod
    def data_model(self) -> type[T]:
        """Specifies the Pydantic model that represents the token's data."""
        raise Exception("No data model specified for this token")

    @abstractmethod
    def to_encode(self, data: U) -> T:
        raise Exception("Not implemented.")

    def encode(self, data: T, expires_delta=timedelta(minutes=15)) -> str:
        """Encodes the token into a JWT string."""

        # Calculate expiration time
        expiration = datetime.now(timezone.utc) + expires_delta

        # Update the expiration in the data model
        data.exp = expiration

        payload = data.model_dump()

        token = jwt.encode(payload, self.key, algorithm="HS256")

        return token

    def decode(self, token: str) -> T:
        """Decodes a given JWT token and validates it against the data model."""
        try:
            payload = jwt.decode(token, self.key, algorithms=["HS256"])

            return self.data_model(**payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token",
                headers={"WWW-Authenticate": "Bearer"},
            )
