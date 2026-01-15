import json
from functools import partial

import anyio.to_thread
import httpx
from astropy.coordinates.name_resolve import (  # type: ignore[import-untyped]
    NameResolveError,
)
from astropy.coordinates.sky_coordinate import SkyCoord  # type: ignore[import-untyped]

from .....core.schemas.coordinate import Coordinate
from .exceptions import NameNotFoundException
from .schemas import NameResolver, NameResolverRead


class NameResolveService:
    """
    Service used to resolve target name into coordinates.

    This service provides methods to resolve a target name into its coordinates
    by either querying the ANTARES broker (for transients with ZTF names) or by
    using the Strasbourg astronomical Data Center (CDS) name resolver.

    Methods
    --------
    resolve(data: NameResolverRead) -> NameResolver
        Resolves a target name into its coordinates and resolver source.
    """

    async def resolve(self, data: NameResolverRead) -> NameResolver:
        if "ztf" in data.name.lower()[:3]:
            coord = await self._antares_resolver("ZTF" + data.name[3:])
            if coord.ra is not None:
                return NameResolver.model_validate(
                    {"ra": coord.ra, "dec": coord.dec, "resolver": "ANTARES"}
                )
        else:
            # Check using the CDS resolver
            try:
                cds_resolve_function = partial(
                    SkyCoord.from_name,
                    name=data.name,
                )
                skycoord = await anyio.to_thread.run_sync(cds_resolve_function)
                if skycoord.ra is not None and skycoord.dec is not None:
                    return NameResolver.model_validate(
                        {
                            "ra": skycoord.ra.deg,
                            "dec": skycoord.dec.deg,
                            "resolver": "CDS",
                        }
                    )

            except NameResolveError:
                raise NameNotFoundException(name=data.name)

        # If no resolution occurred, report a 404 error
        raise NameNotFoundException(name=data.name)

    async def _antares_resolver(self, name: str) -> Coordinate:
        """
        Query ANTARES API to find RA/Dec of a given ZTF source

        Parameters
        ----------
        name: str
            ZTF name of source

        Returns
        -------
            Coordinate schema containing the RA and Dec of the target, if found.

        FIXME: Replace with antares-client module call in future, once confluent-kafka-python issues are resolved.
        """
        ANTARES_URL = "https://api.antares.noirlab.edu/v1/loci"

        search_query = json.dumps(
            {
                "query": {
                    "bool": {"filter": {"term": {"properties.ztf_object_id": name}}}
                }
            }
        )

        params = {
            "sort": "-properties.newest_alert_observation_time",
            "elasticsearch_query[locus_listing]": search_query,
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(ANTARES_URL, params=params)
        r.raise_for_status()

        antares_data = r.json()
        if antares_data["meta"]["count"] > 0:
            ra = antares_data["data"][0]["attributes"]["ra"]
            dec = antares_data["data"][0]["attributes"]["dec"]
        else:
            ra = dec = None

        return Coordinate.model_validate(
            {
                "ra": ra,
                "dec": dec,
            }
        )
