from typing import Generic, Self, TypeVar

from pydantic import Field, computed_field, model_validator

from ...core.schemas.base import BaseSchema


class PaginationParams(BaseSchema):
    page: int | None = Field(default=None, ge=1, description="Page number")
    page_limit: int | None = Field(
        default=None, ge=1, le=10000, description="Records per page"
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def offset(self) -> int | None:
        return (
            (self.page - 1) * self.page_limit
            if self.page is not None and self.page_limit is not None
            else 0
        )

    @model_validator(mode="after")
    def check_required_fields(self) -> Self:
        if not (self.page and self.page_limit) and not (
            not self.page and not self.page_limit
        ):
            raise ValueError("Provide both a page and a page limit or neither")
        return self


T = TypeVar("T")


class Page(BaseSchema, Generic[T]):
    """
    A Pydantic model class representing a returned, paginated list

    Parameters
    ----------
    total_number: int
        the total number of entries before pagination
    page: int
        the page number
    page_limit: int
        the maximum number of entries per page
    items: list[T]
        the queried objects
    """

    total_number: int | None
    page: int | None
    page_limit: int | None
    items: list[T]
