from pydantic import BaseModel


class ConeSearch(BaseModel):
    ra: float
    dec: float
    radius: float
