import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.routes.v1.tools.resolve.schemas import NameResolver


class TestResolveRouter:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
        mock_resolve_params: dict,
    ) -> None:
        self.endpoint = "/tools/resolve-object/"
        self.client = async_client
        self.params = mock_resolve_params

    @pytest.mark.asyncio
    async def test_resolve_should_return_200_when_successful(self) -> None:
        """
        Should return a 200 status code when name successfully resolved
        """
        res = await self.client.get(self.endpoint, params=self.params)
        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_resolve_should_return_name_resolver_when_successful(self) -> None:
        """
        Should return a NameResolver schema when name successfully resolved
        """
        res = await self.client.get(self.endpoint, params=self.params)
        assert NameResolver.model_validate(res.json())
