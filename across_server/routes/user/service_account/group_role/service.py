import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .....db.database import get_session

log = logging.getLogger("uvicorn.error")


class ServiceAccountGroupRoleService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    def assign(self, service_account_id, group_role_id, user_id):
        log.info(
            f"service_account_id: {service_account_id}, group_role_id:{group_role_id}, user_id:{user_id}"
        )
        return ""

    def remove(self, service_account_id, group_role_id, user_id):
        log.info(
            f"service_account_id:{service_account_id}, group_role_id:{group_role_id}, user_id:{user_id}"
        )
        return ""
