import uuid

from across_server.db.models import ObservingProposal

sandy_proposal = ObservingProposal(
    id=uuid.UUID("3da50a07-39fd-4862-acc4-0e57bce144db"),
    name="Sandy's Krusty Krab Proposal",
    code="",
)

observing_proposals = [sandy_proposal]
