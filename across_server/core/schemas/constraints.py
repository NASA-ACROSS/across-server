from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from across_server.core.enums.constraint_type import ConstraintType
from across_server.routes.v1.footprint.schemas import Footprint


class ConstraintReason(BaseModel):
    start_reason: str = Field(..., title="Start Reason")
    end_reason: str = Field(..., title="End Reason")


class Pointing(BaseModel):
    footprint: Footprint
    start_time: str | list[str] = Field(..., title="Start Time")
    end_time: str | list[str] = Field(..., title="End Time")


class Constraint(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: ConstraintType = Field(..., title="Name")
    short_name: str | None = Field(None, title="Short Name")
