import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.db import models
from across_server.routes.permission.service import PermissionService


class TestPermissionService:
    class TestGetAll:
        @pytest.mark.asyncio
        async def test_should_return_permissions_when_successful(
            self,
            mock_db: AsyncMock,
        ) -> None:
            """Should return permissions when is successful"""
            service = PermissionService(mock_db)
            permissions = await service.get_all()
            assert all(
                isinstance(permission, models.Permission) for permission in permissions
            )

    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_permissions_when_successful(
            self,
            mock_db: AsyncMock,
        ) -> None:
            """Should return permissions when is successful"""
            service = PermissionService(mock_db)

            permission_ids: list[uuid.UUID] = [uuid.uuid4()]

            permissions = await service.get_many(permission_ids)
            assert all(
                isinstance(permission, models.Permission) for permission in permissions
            )

        @pytest.mark.asyncio
        async def test_should_select_by_ids_when_present(
            self,
            mock_db: AsyncSession,
        ) -> None:
            """Should select by ids using where clause when ids are present"""
            service = PermissionService(mock_db)

            permission_ids: list[uuid.UUID] = [uuid.uuid4()]

            await service.get_many(permission_ids)
            assert (
                mock_db.execute.call_args[0][0]  # type: ignore[attr-defined]
                .whereclause.clauses[1]
                .right.effective_value
                == permission_ids
            )
