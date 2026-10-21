"""add roman observatory data

Revision ID: dcaee0b5ad32
Revises: 9e16519fbb23
Create Date: 2026-10-21 10:10:55.186828

"""

import uuid
from collections.abc import Sequence
from datetime import datetime

from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums
from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import (
    EarthLimbConstraint,
    MoonAngleConstraint,
    SunAngleConstraint,
)
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_05_26 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observation_strategy import ObservationStrategy
from across_server.core.enums.observatory_type import ObservatoryType
from across_server.core.enums.visibility_type import VisibilityType
from migrations.build_records import ssa_records
from migrations.util.footprint_util import (
    arcsec_to_deg,
    circular_footprint,
)

# revision identifiers, used by Alembic.
revision: str = "dcaee0b5ad32"
down_revision: str | None = "9e16519fbb23"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


"""
NASA's Roman Space Telescope (formerly WFIRST) is a space-based observatory designed to conduct wide-field imaging and surveys in the near-infrared.
"""

"""
Footprint is complicated... calculated from pysiaf (Python library for the Roman Space Telescope's Instrument Aperture File) which provides the geometric layout of the telescope's focal plane and its detectors.
"""
ROMAN_WFI_FOOTPRINT = [
    [
        {"x": 0.019645056578638652, "y": -0.017464008154978353},
        {"x": -0.08689936560983824, "y": 0.04398274434424709},
        {"x": -0.14997311646561684, "y": -0.06465583690173973},
        {"x": -0.04318643715151893, "y": -0.1254738915757598},
        {"x": 0.019645056578638652, "y": -0.017464008154978353},
    ],
    [
        {"x": 0.14503628251363815, "y": -0.09029688642330674},
        {"x": 0.04079512730132835, "y": -0.03019499176624496},
        {"x": -0.021968917894582773, "y": -0.13805698089673515},
        {"x": 0.08262224506009838, "y": -0.19737361513068577},
        {"x": 0.14503628251363815, "y": -0.09029688642330674},
    ],
    [
        {"x": 0.2569313516863751, "y": -0.1553240434394345},
        {"x": 0.15524271169669726, "y": -0.09670588549339738},
        {"x": 0.09285871869891932, "y": -0.20369256924015208},
        {"x": 0.1949911799611193, "y": -0.26138485186548965},
        {"x": 0.2569313516863751, "y": -0.1553240434394345},
    ],
    [
        {"x": -0.07113396017547302, "y": -0.12149887759919004},
        {"x": -0.17826917539480291, "y": -0.06049090857546979},
        {"x": -0.24155077033543648, "y": -0.16837835146024385},
        {"x": -0.1343586790872564, "y": -0.22870942893139826},
        {"x": -0.07113396017547302, "y": -0.12149887759919004},
    ],
    [
        {"x": 0.05466616299998014, "y": -0.19457507190595097},
        {"x": -0.05038437235054971, "y": -0.13503928123821174},
        {"x": -0.11358274846276117, "y": -0.24208548303242725},
        {"x": -0.008355684061598367, "y": -0.300787087242334},
        {"x": 0.05466616299998014, "y": -0.19457507190595097},
    ],
    [
        {"x": 0.1664674004199249, "y": -0.25941480308062626},
        {"x": 0.06378381800424966, "y": -0.20146994928320286},
        {"x": 0.000777401500511975, "y": -0.30758215600653466},
        {"x": 0.10374584522915493, "y": -0.3645686271392418},
        {"x": 0.1664674004199249, "y": -0.25941480308062626},
    ],
    [
        {"x": -0.19527573324455716, "y": -0.20630212432913747},
        {"x": -0.3031299245685659, "y": -0.1454173397828033},
        {"x": -0.36615695667660475, "y": -0.2522319595429254},
        {"x": -0.2584571378591818, "y": -0.31244496358475854},
        {"x": -0.19527573324455716, "y": -0.20630212432913747},
    ],
    [
        {"x": -0.06861631866001972, "y": -0.27991095577349656},
        {"x": -0.17476608981633035, "y": -0.2205392740498792},
        {"x": -0.23797185308626467, "y": -0.3265009794548359},
        {"x": -0.1318547685165754, "y": -0.3850418007846445},
        {"x": -0.06861631866001972, "y": -0.27991095577349656},
    ],
    [
        {"x": 0.04193752018250539, "y": -0.3452342278672522},
        {"x": -0.062201845521826726, "y": -0.28748381070930074},
        {"x": -0.12543594201508768, "y": -0.3925032645336076},
        {"x": -0.02122117814263902, "y": -0.4493036660830364},
        {"x": 0.04193752018250539, "y": -0.3452342278672522},
    ],
    [
        {"x": 0.08696922299485514, "y": 0.09994731423731369},
        {"x": -0.01914408681909663, "y": 0.1619727037024933},
        {"x": -0.08168342910528281, "y": 0.05301516849332911},
        {"x": 0.02483172577991833, "y": -0.008477829191235691},
        {"x": 0.08696922299485514, "y": 0.09994731423731369},
    ],
    [
        {"x": 0.21218412457422048, "y": 0.027002281107771007},
        {"x": 0.10847947977685411, "y": 0.08787951426624531},
        {"x": 0.04643918517482168, "y": -0.02041895516366376},
        {"x": 0.15063998963069863, "y": -0.0805929099706852},
        {"x": 0.21218412457422048, "y": 0.027002281107771007},
    ],
    [
        {"x": 0.3238475567995309, "y": -0.03825847789062004},
        {"x": 0.22278291375393441, "y": 0.021298583608294782},
        {"x": 0.16129263730073737, "y": -0.08622417075364033},
        {"x": 0.2629354648030122, "y": -0.14492920933030537},
        {"x": 0.3238475567995309, "y": -0.03825847789062004},
    ],
    [
        {"x": 0.1307973632065602, "y": 0.23056043689170852},
        {"x": 0.02489281734956097, "y": 0.2931845165040954},
        {"x": -0.03690559384972403, "y": 0.18438680061731894},
        {"x": 0.06954124236302087, "y": 0.12215928880248217},
        {"x": 0.1307973632065602, "y": 0.23056043689170852},
    ],
    [
        {"x": 0.2562783884452221, "y": 0.15752276338801818},
        {"x": 0.15278498053265593, "y": 0.2192593229086485},
        {"x": 0.09165520627513596, "y": 0.11096246424100392},
        {"x": 0.19577652051956143, "y": 0.04980848908864461},
        {"x": 0.2562783884452221, "y": 0.15752276338801818},
    ],
    [
        {"x": 0.36761942135410824, "y": 0.09236806791802618},
        {"x": 0.2667404407458952, "y": 0.15301487463155825},
        {"x": 0.20631560590345305, "y": 0.04536075176324505},
        {"x": 0.3078722259279283, "y": -0.014554674786137997},
        {"x": 0.36761942135410824, "y": 0.09236806791802618},
    ],
    [
        {"x": 0.14126820923782574, "y": 0.37995174393269815},
        {"x": 0.035207314478851705, "y": 0.4430884825334982},
        {"x": -0.02580416794626217, "y": 0.3350196168915989},
        {"x": 0.08091071519956793, "y": 0.27208722271951935},
        {"x": 0.14126820923782574, "y": 0.37995174393269815},
    ],
    [
        {"x": 0.26751870631336916, "y": 0.30664215118405735},
        {"x": 0.16369937028340067, "y": 0.3692383892330918},
        {"x": 0.10350539901287556, "y": 0.2614587270541685},
        {"x": 0.20804815808094076, "y": 0.19925282043617124},
        {"x": 0.26751870631336916, "y": 0.30664215118405735},
    ],
    [
        {"x": 0.3785554763688126, "y": 0.24300210755059026},
        {"x": 0.2771898923670507, "y": 0.30482059008671275},
        {"x": 0.2178197960752419, "y": 0.19748909038583795},
        {"x": 0.31995562951061685, "y": 0.1362103741026993},
        {"x": 0.3785554763688126, "y": 0.24300210755059026},
    ],
]

WFI_F062_BANDPASS = WavelengthBandpass(
    filter_name="WFI_F062",
    min=4800,
    max=7600,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_F087_BANDPASS = WavelengthBandpass(
    filter_name="WFI_F087",
    min=7600,
    max=9770,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_F106_BANDPASS = WavelengthBandpass(
    filter_name="WFI_F106",
    min=9270,
    max=11920,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_F129_BANDPASS = WavelengthBandpass(
    filter_name="WFI_F129",
    min=11310,
    max=14540,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_F158_BANDPASS = WavelengthBandpass(
    filter_name="WFI_F158",
    min=13800,
    max=17740,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_F184_BANDPASS = WavelengthBandpass(
    filter_name="WFI_F184",
    min=16830,
    max=20000,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_F213_BANDPASS = WavelengthBandpass(
    filter_name="WFI_F213",
    min=19500,
    max=23000,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_F146_BANDPASS = WavelengthBandpass(
    filter_name="WFI_F146",
    min=9270,
    max=20000,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_G150_BANDPASS = WavelengthBandpass(
    filter_name="WFI_G150",
    min=10000,
    max=19300,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
WFI_P127_BANDPASS = WavelengthBandpass(
    filter_name="WFI_P127",
    min=7500,
    max=18000,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

"""
Coronograph Instrument - CGI (Coronagraph Instrument) on the Roman Space Telescope is designed for high-contrast imaging to directly observe exoplanets and circumstellar disks. It uses a combination of coronagraphic masks and wavefront control to suppress starlight and enhance the visibility of faint companions.

7.2 arcseconds in diameter

4 science bandpasses
"""

CGI_FOOTPRINT = circular_footprint(arcsec_to_deg(7.2))

CG1_BAND1_BANDPASS = WavelengthBandpass(
    filter_name="CG1_BAND1",
    min=5460,
    max=6040,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
CG1_BAND2_BANDPASS = WavelengthBandpass(
    filter_name="CG1_BAND2",
    min=6100,
    max=7100,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
CG1_BAND3_BANDPASS = WavelengthBandpass(
    filter_name="CG1_BAND3",
    min=6750,
    max=7850,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)
CG1_BAND4_BANDPASS = WavelengthBandpass(
    filter_name="CG1_BAND4",
    min=7830,
    max=8670,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

OBSERVATORY: dict = {
    "id": uuid.UUID("62516d62-91fd-473a-9a2c-317d0eee9cb4"),
    "name": "Nancy Grace Roman Space Telescope",
    "short_name": "ROMAN",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://science.nasa.gov/mission/roman-space-telescope/",
    "operational_begin_date": datetime(2026, 12, 25, 0, 0, 0),  # noqa: DTZ001
    "telescopes": [
        {
            "id": uuid.UUID("8688a773-68b8-42fd-8b15-2a04028a5ee1"),
            "name": "Nancy Grace Roman Space Telescope",
            "short_name": "ROMAN",
            "is_operational": True,
            "is_observation_request_enabled": False,
            "reference_url": "https://science.nasa.gov/mission/roman-space-telescope/",
            "instruments": [
                {
                    "id": uuid.UUID("fa2e565a-a88d-4637-b238-5ddd6c2e0057"),
                    "name": "Wide Field Instrument",
                    "short_name": "WFI",
                    "type": InstrumentType.IMAGING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": ROMAN_WFI_FOOTPRINT,
                    "reference_url": "https://science.nasa.gov/mission/roman-space-telescope/wfi-technical/",
                    "visibility_type": VisibilityType.EPHEMERIS.value,
                    "observation_strategy": ObservationStrategy.SURVEY.value,
                    "filters": [
                        {
                            "id": uuid.UUID("53de0ed3-e555-4b61-87af-61fd8e4534bf"),
                            "name": WFI_F062_BANDPASS.filter_name,
                            "min_wavelength": WFI_F062_BANDPASS.min,
                            "max_wavelength": WFI_F062_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("3c00476a-4762-451e-b197-44c41da15bc7"),
                            "name": WFI_F087_BANDPASS.filter_name,
                            "min_wavelength": WFI_F087_BANDPASS.min,
                            "max_wavelength": WFI_F087_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("93b411d0-d5bb-4d10-9c17-59872d0e0e81"),
                            "name": WFI_F106_BANDPASS.filter_name,
                            "min_wavelength": WFI_F106_BANDPASS.min,
                            "max_wavelength": WFI_F106_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("16951336-4c11-493d-8461-51de39218942"),
                            "name": WFI_F129_BANDPASS.filter_name,
                            "min_wavelength": WFI_F129_BANDPASS.min,
                            "max_wavelength": WFI_F129_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("46c1aee4-d794-4c51-a430-3acac335d1c7"),
                            "name": WFI_F158_BANDPASS.filter_name,
                            "min_wavelength": WFI_F158_BANDPASS.min,
                            "max_wavelength": WFI_F158_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("6bf1fac9-9b49-4a55-be63-91c7fece224a"),
                            "name": WFI_F184_BANDPASS.filter_name,
                            "min_wavelength": WFI_F184_BANDPASS.min,
                            "max_wavelength": WFI_F184_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("ac8b790d-1ea0-4bff-91a8-fe0aef0bd9a4"),
                            "name": WFI_F213_BANDPASS.filter_name,
                            "min_wavelength": WFI_F213_BANDPASS.min,
                            "max_wavelength": WFI_F213_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("a3e1db13-e42e-40f1-b747-09e149e55602"),
                            "name": WFI_G150_BANDPASS.filter_name,
                            "min_wavelength": WFI_G150_BANDPASS.min,
                            "max_wavelength": WFI_G150_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("3dfccb9d-7de6-4db7-89c0-c0915ad20ccc"),
                            "name": WFI_P127_BANDPASS.filter_name,
                            "min_wavelength": WFI_P127_BANDPASS.min,
                            "max_wavelength": WFI_P127_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("7352fb99-9e53-4612-aec4-7d3a7ebdf985"),
                    "name": "Coronagraph Instrument",
                    "short_name": "CGI",
                    "type": InstrumentType.IMAGING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": CGI_FOOTPRINT,
                    "reference_url": "https://assets.science.nasa.gov/content/dam/science/missions/rst/science/Roman-CGI-Reference-Info-January2025.pdf",
                    "visibility_type": VisibilityType.EPHEMERIS.value,
                    "observation_strategy": ObservationStrategy.SURVEY.value,
                    "filters": [
                        {
                            "id": uuid.UUID("4f85615b-3fae-4e0d-aa8d-fb12d1a80be4"),
                            "name": CG1_BAND1_BANDPASS.filter_name,
                            "min_wavelength": CG1_BAND1_BANDPASS.min,
                            "max_wavelength": CG1_BAND1_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("5d516408-13c1-4139-8eed-e2086c70d3e6"),
                            "name": CG1_BAND2_BANDPASS.filter_name,
                            "min_wavelength": CG1_BAND2_BANDPASS.min,
                            "max_wavelength": CG1_BAND2_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("ab328472-341f-45ca-b993-db9a5c04e676"),
                            "name": CG1_BAND3_BANDPASS.filter_name,
                            "min_wavelength": CG1_BAND3_BANDPASS.min,
                            "max_wavelength": CG1_BAND3_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("a8d6a250-896c-4333-b957-1b744e7db21e"),
                            "name": CG1_BAND4_BANDPASS.filter_name,
                            "min_wavelength": CG1_BAND4_BANDPASS.min,
                            "max_wavelength": CG1_BAND4_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
            ],
            "constraints": [
                # Not sure if this is the best way to do this - I found the sun constraint for the WFI and the Earth/Moon constraints from the cgi documentation.
                {
                    "id": uuid.UUID("33b87a35-7ce9-4678-9b12-2f6eb2f09cdf"),
                    "constraint_type": ConstraintType.SUN,
                    "constraint_parameters": SunAngleConstraint(
                        min_angle=54.0,
                        max_angle=126.0,
                    ).model_dump(),
                },
                {
                    "id": uuid.UUID("77f5424e-dff5-4754-b83d-98022968f2d3"),
                    "constraint_type": ConstraintType.MOON,
                    "constraint_parameters": MoonAngleConstraint(
                        min_angle=11.0,
                    ).model_dump(),
                },
                {
                    "id": uuid.UUID("004a1d93-52ea-4d24-b872-aaa0ecabfa69"),
                    "constraint_type": ConstraintType.EARTH,
                    "constraint_parameters": EarthLimbConstraint(
                        min_angle=22.0,
                    ).model_dump(),
                },
            ],
        },
    ],
    "ephemeris_types": [
        # If an Earth orbiting spacecraft lacks a DSN identification code, the NAIF ID is derived from the tracking ID assigned to it by NORAD via:
        # NAIF ID = -100000 - NORAD ID code
        {
            "id": uuid.UUID("6b2f1fe6-0f8f-4edf-8a46-14c885f5d8ed"),
            "ephemeris_type": EphemerisType.JPL,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("79ce5e4c-96d6-4c17-8371-9948289e815a"),
                "naif_id": -200532,
            },
        },
        {
            "id": uuid.UUID("e1b31f8a-b6c5-4d67-b38a-6e6b7e2ad0b1"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 2,
            "parameters": {
                "id": uuid.UUID("86559989-ed59-46d6-8491-505a00504ffa"),
                "norad_id": 100532,
                "norad_satellite_name": "NGRST",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("e14c5430-bd3c-44df-b286-a27cefaaaa2a"),
        "name": "Nancy Grace Roman Space Telescope",
        "short_name": "ROMAN",
        "group_admin": {
            "id": uuid.UUID("d85016ea-3ce6-4931-8cfc-cebd7a94c6bf"),
            "name": "ROMAN Group Admin",
        },
    },
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    records = ssa_records.build(session, OBSERVATORY, snapshot_models)

    session.add_all(records)
    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    ssa_records.delete(session, OBSERVATORY, snapshot_models)

    session.commit()
