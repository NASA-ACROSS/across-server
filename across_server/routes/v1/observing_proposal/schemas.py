import uuid

from ....core.schemas.base import BaseSchema


class ObservingProposalBase(BaseSchema):
    name: str
    code: str


class ObservingProposalCreate(ObservingProposalBase):
    id: uuid.UUID | None = None


class ObservingProposal(ObservingProposalBase):
    id: uuid.UUID
