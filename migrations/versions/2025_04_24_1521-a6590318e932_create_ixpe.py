"""create ixpe

Revision ID: a6590318e932
Revises: e4ec21aebc19
Create Date: 2025-04-24 15:21:03.729061

"""

from __future__ import annotations

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
from sqlalchemy import orm, select

from migrations.versions.model_snapshots.models_2025_04_24 import (
    ACROSSFootprintPoint,
    Footprint,
    Group,
    Instrument,
    Observatory,
    Telescope,
    create_geography,
)

# revision identifiers, used by Alembic.
revision: str = "a6590318e932"
down_revision: Union[str, None] = "e4ec21aebc19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def arcmin_to_deg(arcmin: float) -> float:
    """Convert arcminute to degrees."""
    return arcmin / 60.0


# 12 arcmin x 12 arcmin square
footprint: list[list[dict]] = [
    [
        {"x": arcmin_to_deg(-6.0), "y": arcmin_to_deg(-6.0)},
        {"x": arcmin_to_deg(6.0), "y": arcmin_to_deg(-6.0)},
        {"x": arcmin_to_deg(6.0), "y": arcmin_to_deg(6.0)},
        {"x": arcmin_to_deg(-6.0), "y": arcmin_to_deg(6.0)},
        {"x": arcmin_to_deg(-6.0), "y": arcmin_to_deg(-6.0)},
    ]
]

OBSERVATORY = {
    "name": "Imaging X-Ray Polarimetry Explorer",
    "short_name": "IXPE",
    "observatory_type": "SPACE_BASED",
    "reference_url": "https://ixpe.msfc.nasa.gov/index.html",
    "telescopes": [
        {
            "name": "Imaging X-Ray Polarimetry Explorer",
            "short_name": "IXPE",
            "instruments": [
                {
                    "name": "Imaging X-Ray Polarimetry Explorer",
                    "short_name": "IXPE",
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/heasarc/missions/ixpe.html",
                    "footprint": footprint,
                }
            ],
        }
    ],
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    # create group based off the observatory
    group = Group(
        id=uuid4(), name=OBSERVATORY["name"], short_name=OBSERVATORY["short_name"]
    )
    session.add(group)

    # # create observatory
    observatory_insert = Observatory(
        id=uuid4(),
        name=OBSERVATORY["name"],
        short_name=OBSERVATORY["short_name"],
        type=OBSERVATORY["observatory_type"],
        group=group,
    )
    session.add(observatory_insert)
    observatory_id = observatory_insert.id

    # get the telescopes
    telescopes = OBSERVATORY["telescopes"]
    for telescope in telescopes:
        # create the telescope record
        telescope_insert = Telescope(
            id=uuid4(),
            name=telescope["name"],  #  type:ignore
            short_name=telescope["short_name"],  #  type:ignore
            observatory_id=observatory_id,
        )
        session.add(telescope_insert)
        telescope_id = telescope_insert.id

        # get the instruments
        instruments = telescope["instruments"]  #  type:ignore
        for instrument in instruments:
            # create the instrument record
            instrument_insert = Instrument(
                id=uuid4(),
                name=instrument["name"],  #  type:ignore
                short_name=instrument["short_name"],  #  type:ignore
                telescope_id=telescope_id,
            )
            session.add(instrument_insert)
            instrument_id = instrument_insert.id

            footprints = instrument["footprint"]
            for footprint in footprints:
                # convert the input footprint to the string polygon
                vertices = []
                for point in footprint:
                    vertices.append(ACROSSFootprintPoint(x=point["x"], y=point["y"]))

                polygon = create_geography(polygon=vertices)

                # create the footprint model record
                footprint_insert = Footprint(
                    polygon=polygon, instrument_id=instrument_id
                )
                session.add(footprint_insert)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    group = session.scalar(select(Group).filter_by(name=OBSERVATORY["name"]))
    observatory = session.scalar(
        select(Observatory).filter_by(name=OBSERVATORY["name"])
    )

    session.delete(group)
    session.delete(observatory)

    session.commit()
    # fin
