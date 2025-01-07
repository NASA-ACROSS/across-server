import json

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestObservationPostRoute:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, mock_observation_data: dict):
        self.client = async_client
        self.endpoint = "/observation/"
        self.data = mock_observation_data

    @pytest.mark.asyncio
    async def test_should_return_200_on_success(self):
        """Should return a 200 when successful"""
        res = await self.client.post(self.endpoint, json=self.data)
        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_return_created_observation_on_success(self):
        """Should return created observation when successful"""
        res = await self.client.post(self.endpoint, json=self.data)
        assert json.loads(res.text)["description"] == "the returned observation"

    @pytest.mark.asyncio
    async def test_should_create_observation_once(self, mock_observation_service):
        """Should call the observation create endpoint once"""
        await self.client.post(self.endpoint, json=self.data)
        mock_observation_service.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_422_when_missing_instrument_id(self):
        """Should return a 422 when the input is missing the instrument ID"""
        self.data.pop("instrument_id")
        res = await self.client.post(self.endpoint, json=self.data)

        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_should_return_422_when_missing_schedule_id(self):
        """Should return a 422 when the input is missing the schedule ID"""
        self.data.pop("schedule_id")
        res = await self.client.post(self.endpoint, json=self.data)

        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_should_return_422_when_missing_object_name(self):
        """Should return a 422 when the input is missing the object name"""
        self.data.pop("object_name")
        res = await self.client.post(self.endpoint, json=self.data)

        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_should_return_422_when_missing_pointing_position(self):
        """Should return a 422 when the input is missing the pointing position"""
        self.data.pop("pointing_position")
        res = await self.client.post(self.endpoint, json=self.data)

        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_should_return_422_when_missing_date_range(self):
        """Should return a 422 when the input is missing the date range"""
        self.data.pop("date_range")
        res = await self.client.post(self.endpoint, json=self.data)

        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_should_return_422_when_missing_external_observation_id(self):
        """Should return a 422 when the input is missing the external observation ID"""
        self.data.pop("external_observation_id")
        res = await self.client.post(self.endpoint, json=self.data)

        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_should_return_422_when_missing_type(self):
        """Should return a 422 when the input is missing the type"""
        self.data.pop("type")
        res = await self.client.post(self.endpoint, json=self.data)

        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_should_return_422_when_missing_status(self):
        """Should return a 422 when the input is missing the status"""
        self.data.pop("status")
        res = await self.client.post(self.endpoint, json=self.data)

        assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
