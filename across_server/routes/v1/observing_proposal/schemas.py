import uuid

from ....core.schemas.base import BaseSchema


class ObservingProposalBase(BaseSchema):
    name: str
    code: str


class ObservingProposalCreate(ObservingProposalBase):
    pass


class ObservingProposal(ObservingProposalBase):
    id: uuid.UUID
