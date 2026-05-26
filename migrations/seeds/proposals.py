import uuid

from across_server.db.models import Proposal

sandy_proposal = Proposal(
    id=uuid.UUID("3da50a07-39fd-4862-acc4-0e57bce144db"),
    name="Sandy's Krusty Krab Proposal",
    code="",
)

proposals = [sandy_proposal]
