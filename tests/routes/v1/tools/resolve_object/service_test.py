from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from astropy.coordinates.name_resolve import (  # type: ignore[import-untyped]
    NameResolveError,
)
from astropy.coordinates.sky_coordinate import SkyCoord  # type: ignore[import-untyped]

import across_server.routes.v1.tools.resolve_object.service as service_mod
from across_server.core.schemas import Coordinate
from across_server.routes.v1.tools.resolve_object.exceptions import (
    NameNotFoundException,
)
from across_server.routes.v1.tools.resolve_object.schemas import (
    NameResolver,
    NameResolverRead,
)
from across_server.routes.v1.tools.resolve_object.service import NameResolveService


class TestNameResolveService:
    @pytest.mark.asyncio
    async def test_service_should_use_antares_if_ztf_name(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_coordinate: Coordinate,
        mock_ztf_resolve_input: NameResolverRead,
    ) -> None:
        """Should use the ANTARES API if the name is a ZTF name"""
        mock_antares_resolver = AsyncMock(return_value=mock_coordinate)
        monkeypatch.setattr(
            NameResolveService, "_antares_resolver", mock_antares_resolver
        )

        await NameResolveService().resolve(data=mock_ztf_resolve_input)
        mock_antares_resolver.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_should_return_name_resolver_schema_when_using_antares(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_coordinate: Coordinate,
        mock_ztf_resolve_input: NameResolverRead,
    ) -> None:
        """Should return a NameResolver schema when using ANTARES"""
        mock_antares_resolver = AsyncMock(return_value=mock_coordinate)
        monkeypatch.setattr(
            NameResolveService, "_antares_resolver", mock_antares_resolver
        )

        res = await NameResolveService().resolve(data=mock_ztf_resolve_input)
        assert NameResolver.model_validate(res)

    @pytest.mark.asyncio
    async def test_service_should_raise_exception_if_coordinates_not_found(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_null_coordinate: Coordinate,
        mock_ztf_resolve_input: NameResolverRead,
    ) -> None:
        """Should raise a NameNotFoundException if ANTARES does resolve name"""
        mock_antares_resolver = AsyncMock(return_value=mock_null_coordinate)
        monkeypatch.setattr(
            NameResolveService, "_antares_resolver", mock_antares_resolver
        )

        with pytest.raises(NameNotFoundException):
            await NameResolveService().resolve(data=mock_ztf_resolve_input)

    @pytest.mark.asyncio
    async def test_service_should_use_cds_if_not_ztf_name(
        self, monkeypatch: pytest.MonkeyPatch, mock_resolve_input: NameResolverRead
    ) -> None:
        """Should use the CDS resolver if the name is not a ZTF name"""
        mock_partial = MagicMock()
        monkeypatch.setattr(service_mod, "partial", mock_partial)

        await NameResolveService().resolve(data=mock_resolve_input)
        mock_partial.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_should_return_name_resolver_schema_when_using_cds(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_skycoord: SkyCoord,
        mock_resolve_input: NameResolverRead,
    ) -> None:
        """Should return a NameResolver schema when using CDS"""
        mock_run = AsyncMock(return_value=mock_skycoord)
        monkeypatch.setattr(service_mod.anyio.to_thread, "run_sync", mock_run)

        res = await NameResolveService().resolve(data=mock_resolve_input)
        assert NameResolver.model_validate(res)

    @pytest.mark.asyncio
    async def test_service_should_raise_exception_if_cds_fails(
        self, monkeypatch: pytest.MonkeyPatch, mock_resolve_input: NameResolverRead
    ) -> None:
        """Should raise a NameNotFoundException if CDS raises an error"""
        mock_run = AsyncMock(side_effect=NameResolveError)
        monkeypatch.setattr(service_mod.anyio.to_thread, "run_sync", mock_run)

        with pytest.raises(NameNotFoundException):
            await NameResolveService().resolve(data=mock_resolve_input)

    @pytest.mark.asyncio
    async def test_antares_resolver_should_return_coordinate(
        self,
        mock_resolve_input: NameResolverRead,
    ) -> None:
        """ANTARES resolver should return Coordinate schema"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "meta": {"count": 1},
            "data": [
                {
                    "attributes": {
                        "ra": 123.45,
                        "dec": -43.21,
                    },
                },
            ],
        }

        with patch(
            "across_server.routes.v1.tools.resolve_object.service.httpx.AsyncClient.get",
            return_value=mock_response,
        ):
            coord = await NameResolveService()._antares_resolver(
                mock_resolve_input.object_name
            )
            assert Coordinate.model_validate(coord)
