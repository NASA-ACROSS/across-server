from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.routes.v1.tools.visibility_calculator.schemas import (
    JointVisibilityResult,
    VisibilityResult,
)


class TestVisibilityCalculatorRouter:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
        fake_instrument_id: UUID,
    ) -> None:
        self.client = async_client
        self.endpoint = f"/tools/visibility-calculator/windows/{fake_instrument_id}"

    @pytest.mark.asyncio
    async def test_get_should_return_404_when_instrument_has_no_telescope(
        self,
        mock_instrument_service: AsyncMock,
        fake_instrument_schema_from_orm: MagicMock,
        fake_visibility_read_params: dict,
    ) -> None:
        """Should return a 404 status when instrument has no associated telescope"""
        fake_instrument_schema_from_orm.telescope = None
        mock_instrument_service.get.return_value = fake_instrument_schema_from_orm

        res = await self.client.get(
            self.endpoint,
            params=fake_visibility_read_params,
        )
        assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_should_return_200_when_successful(
        self,
        fake_visibility_read_params: dict,
    ) -> None:
        """Should return a 200 status when successful"""
        res = await self.client.get(
            self.endpoint,
            params=fake_visibility_read_params,
        )
        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_should_return_visibility_result(
        self,
        fake_visibility_read_params: dict,
    ) -> None:
        """Should return a VisibilityResult when successful"""
        res = await self.client.get(
            self.endpoint,
            params=fake_visibility_read_params,
        )
        assert VisibilityResult.model_validate(res.json())


class TestJointVisibilityCalculatorRouter:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
    ) -> None:
        self.client = async_client
        self.endpoint = "/tools/visibility-calculator/windows/"

    @pytest.mark.asyncio
    async def test_get_should_return_404_when_instrument_has_no_telescope(
        self,
        mock_instrument_service: AsyncMock,
        fake_instrument_schema_from_orm: MagicMock,
        fake_joint_visibility_read_params: dict,
    ) -> None:
        """Should return a 404 status when any instrument has no associated telescope"""
        fake_instrument_schema_from_orm.telescope = None
        mock_instrument_service.get.return_value = fake_instrument_schema_from_orm

        res = await self.client.get(
            self.endpoint,
            params=fake_joint_visibility_read_params,
        )
        assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_should_return_200_when_successful(
        self,
        fake_joint_visibility_read_params: dict,
    ) -> None:
        """Should return a 200 status when successful"""
        res = await self.client.get(
            self.endpoint,
            params=fake_joint_visibility_read_params,
        )
        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_should_return_joint_visibility_result(
        self,
        fake_joint_visibility_read_params: dict,
    ) -> None:
        """Should return a JointVisibilityResult when successful"""
        res = await self.client.get(
            self.endpoint,
            params=fake_joint_visibility_read_params,
        )
        assert JointVisibilityResult.model_validate(res.json())

    @pytest.mark.asyncio
    async def test_get_should_return_422_when_params_invalid(
        self,
        fake_joint_visibility_read_params: dict,
    ) -> None:
        """Should return a 422 status code when parameters are invalid"""
        fake_joint_visibility_read_params["instrument_ids"] = []
        res = await self.client.get(
            self.endpoint,
            params=fake_joint_visibility_read_params,
        )
        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
