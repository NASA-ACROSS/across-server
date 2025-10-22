"""Keck observatory data

Revision ID: 161e7121bdbf
Revises: 9c6db8cdfe82
Create Date: 2025-10-08 11:16:45.645282

"""

import uuid
from datetime import datetime
from typing import Sequence, Union

from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums
from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import AltAzConstraint
from alembic import op
from shapely import Polygon
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_10_03 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observatory_type import ObservatoryType
from across_server.core.enums.visibility_type import VisibilityType
from migrations.build_records import ssa_records
from migrations.util.footprint_util import (
    arcmin_to_deg,
    arcsec_to_deg,
    project_footprint,
    rectangle_footprint,
    square_footprint,
)

# revision identifiers, used by Alembic.
revision: str = "161e7121bdbf"
down_revision: Union[str, None] = "50c390eb41cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""
HIRES is a high resolution echelle spectrograph on Keck I
"""

HIRES_BANDPASS = WavelengthBandpass(
    filter_name="HIRES",
    min=3000,
    max=11000,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

"""
LRIS is a low-resolution spectrograph and imager on Keck I

LRIS footprint is made up of 2 6'x8' CCDs
with a 13.5" chip gap between them.
To model the footprint we will translate a single rectangular ccd footprint 2 times:
"""
lris_ccd = rectangle_footprint(
    width_deg=arcmin_to_deg(8.0),
    height_deg=arcmin_to_deg(6.0),
)
LRIS_FOOTPRINT = [
    # top: dx=0, dy=8' + 13.5"/2
    project_footprint(
        lris_ccd,
        ra_deg=0,
        dec_deg=arcmin_to_deg(6.0 / 2) + arcsec_to_deg(13.5 / 2),
    )[0],
    # bottom: dx=0, dy=-(8' + 13.5"/2)
    project_footprint(
        lris_ccd,
        ra_deg=0,
        dec_deg=-(arcmin_to_deg(6.0 / 2) + arcsec_to_deg(13.5 / 2)),
    )[0],
]

# LRIS bandpass information taken from:
# https://www2.keck.hawaii.edu/inst/lris/filters.html#footnote_1B
# Note that the blue and red arms have slightly different filter curves,
# but here I approximate them as the same for simplicity
LRIS_BANDPASS = WavelengthBandpass(
    filter_name="LRIS",
    min=3200,
    max=10000,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_U_BANDPASS = WavelengthBandpass(
    filter_name="u'",
    central_wavelength=3450,
    bandwidth=525,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_B_BANDPASS = WavelengthBandpass(
    filter_name="B",
    central_wavelength=4370,
    bandwidth=878,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_G_BANDPASS = WavelengthBandpass(
    filter_name="g",
    central_wavelength=4731,
    bandwidth=1082,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_V_BANDPASS = WavelengthBandpass(
    filter_name="V",
    central_wavelength=5437,
    bandwidth=922,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_R_BANDPASS = WavelengthBandpass(
    filter_name="R",
    central_wavelength=6417,
    bandwidth=1185,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_RS_BANDPASS = WavelengthBandpass(
    filter_name="Rs",
    central_wavelength=6809,
    bandwidth=1269,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_I_BANDPASS = WavelengthBandpass(
    filter_name="I",
    central_wavelength=7599,
    bandwidth=1225,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

"""
NIRC2 is an infrared imager and low-resolution spectrograph on Keck II
"""

# From https://www2.keck.hawaii.edu/inst/nirc2/genspecs.html
NIRC2_FOOTPRINT = square_footprint(length_deg=arcsec_to_deg(40.0))

# Filter info here: https://www2.keck.hawaii.edu/inst/nirc2/filters.html
# Below are the broadband filters
NIRC2_Z_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 z",
    central_wavelength=1.0311,
    bandwidth=0.0481,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_Y_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Y",
    central_wavelength=1.018,
    bandwidth=0.0996,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_J_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 J",
    central_wavelength=1.248,
    bandwidth=0.163,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_H_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 H",
    central_wavelength=1.633,
    bandwidth=0.296,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_K_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 K",
    central_wavelength=2.196,
    bandwidth=0.336,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_KS_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Ks",
    central_wavelength=2.146,
    bandwidth=0.311,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_KP_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Kp",
    central_wavelength=2.124,
    bandwidth=0.351,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_LW_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Lw",
    central_wavelength=3.5197,
    bandwidth=1.3216,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_LP_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Lp",
    central_wavelength=3.776,
    bandwidth=0.7,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_MS_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Ms",
    central_wavelength=4.67,
    bandwidth=0.241,
    unit=tools_enums.WavelengthUnit.MICRON,
)

"""
NIRSPEC is a near-infrared echelle spectrograph on Keck II
"""

NIRSPEC_BANDPASS = WavelengthBandpass(
    filter_name="NIRSPEC Bandpass",
    min=0.96,
    max=5.5,
    unit=tools_enums.WavelengthUnit.MICRON,
)

"""
ESI is an optical imager and spectrograph on Keck II
"""

ESI_FOOTPRINT = rectangle_footprint(
    width_deg=arcmin_to_deg(8.0), height_deg=arcmin_to_deg(2.0)
)

ESI_BANDPASS = WavelengthBandpass(
    filter_name="ESI Bandpass",
    min=3900,
    max=10900,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

# From SVO filter service

ESI_B_BANDPASS = WavelengthBandpass(
    filter_name="ESI B",
    min=3733,
    max=5413,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

ESI_V_BANDPASS = WavelengthBandpass(
    filter_name="ESI V",
    min=4887,
    max=6398,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

ESI_R_BANDPASS = WavelengthBandpass(
    filter_name="ESI R",
    min=5990,
    max=7424,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

"""
DEIMOS is an optical multi-object spectrograph and imager on Keck II

DEIMOS's footprint is a series of 4 4.075' x 5' rectangles with
0.1' x 5' chip gaps and two cut off upper corners.
For our purposes, let's just model it by translating the same rectangular
CCD 4 times, accounting for the chip gaps.
    -----  ----- ----- -----
    |   |  |   | |   | |   | 5'
    -----  ----- ----- -----
                       4.075'

Assuming the center is at (0,0), then the leftmost ccd is translated by
dx = -(4.075/2 + 0.1/2 + 4.075 + 0.1)',
the left middle ccd is translated by
dx = -(4.075/2 + 0.1/2)',
the right middle ccd is translated by
dx = (4.075/2 + 0.1/2)',
and the rightmost ccd is translated by
dx = (4.075/2 + 0.1/2 + 4.075 + 0.1)'
"""

deimos_ccd = rectangle_footprint(
    width_deg=arcmin_to_deg(4.075), height_deg=arcmin_to_deg(5.0)
)

DEIMOS_FOOTPRINT = [
    # From left to right
    project_footprint(
        deimos_ccd,
        ra_deg=-arcmin_to_deg(4.075 / 2 + 0.1 / 2 + 4.075 + 0.1),
        dec_deg=0,
    )[0],
    project_footprint(
        deimos_ccd,
        ra_deg=-arcmin_to_deg(4.075 / 2 + 0.1 / 2),
        dec_deg=0,
    )[0],
    project_footprint(
        deimos_ccd,
        ra_deg=arcmin_to_deg(4.075 / 2 + 0.1 / 2),
        dec_deg=0,
    )[0],
    project_footprint(
        deimos_ccd,
        ra_deg=arcmin_to_deg(4.075 / 2 + 0.1 / 2 + 4.075 + 0.1),
        dec_deg=0,
    )[0],
]

DEIMOS_BANDPASS = WavelengthBandpass(
    filter_name="ESI Bandpass",
    min=4100,
    max=11000,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

# From https://www2.keck.hawaii.edu/inst/deimos/filter_list.html

DEIMOS_B_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS B Bandpass",
    central_wavelength=4416,
    bandwidth=373,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_V_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS V Bandpass",
    central_wavelength=5452,
    bandwidth=628,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_R_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS R Bandpass",
    central_wavelength=6487,
    bandwidth=810,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_I_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS I Bandpass",
    central_wavelength=8390,
    bandwidth=1689,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_Z_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS B Bandpass",
    central_wavelength=9085,
    bandwidth=969,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

"""
KCWI is an IFU spectrograph on Keck II
"""

# KCWI has a variable FOV, so let's define it as the biggest possible
KCWI_FOOTPRINT = rectangle_footprint(
    width_deg=arcsec_to_deg(20), height_deg=arcsec_to_deg(33)
)

KCWI_BANDPASS = WavelengthBandpass(
    filter_name="KCWI Bandpass",
    min=3500,
    max=10800,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

"""
KPF is a high resolution echelle spectrograph on Keck I
"""

KPF_BANDPASS = WavelengthBandpass(
    filter_name="KPF Bandpass",
    min=4400,
    max=8500,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

"""
MOSFIRE is a multi-object NIR spectrograph on Keck I
"""

MOSFIRE_FOOTPRINT = square_footprint(length_deg=arcmin_to_deg(6.1))

# Grating info here: https://www2.keck.hawaii.edu/inst/mosfire/grating.html

MOSFIRE_Y_BANDPASS = WavelengthBandpass(
    filter_name="MOSFIRE Y Bandpass",
    min=0.9716,
    max=1.125,
    unit=tools_enums.WavelengthUnit.MICRON,
)

MOSFIRE_J_BANDPASS = WavelengthBandpass(
    filter_name="MOSFIRE J Bandpass",
    min=1.153,
    max=1.352,
    unit=tools_enums.WavelengthUnit.MICRON,
)

MOSFIRE_H_BANDPASS = WavelengthBandpass(
    filter_name="MOSFIRE H Bandpass",
    min=1.468,
    max=1.804,
    unit=tools_enums.WavelengthUnit.MICRON,
)

MOSFIRE_K_BANDPASS = WavelengthBandpass(
    filter_name="MOSFIRE Y Bandpass",
    min=1.954,
    max=2.397,
    unit=tools_enums.WavelengthUnit.MICRON,
)

"""
NIRES is a NIR echelle spectrograph on Keck II
"""

NIRES_BANDPASS = WavelengthBandpass(
    filter_name="NIRES Bandpass",
    min=0.94,
    max=2.45,
    unit=tools_enums.WavelengthUnit.MICRON,
)

"""
Define AltAzConstraints for Keck I and II based on polygon avoidance
as well as min/max constraints.
From https://www2.keck.hawaii.edu/observing/kecktelgde/ktelinstupdate.pdf
"""

keck_i_altaz_polygon_restriction = Polygon(
    [
        [18.0, 5.3],
        [33.3, 5.3],
        [33.3, 146.2],
        [18.0, 146.2],
        [18.0, 5.3],
    ]
)

keck_i_alt_min = 18.0
keck_i_alt_max = 88.9

KECK_I_ALTAZ_CONSTRAINT = AltAzConstraint(
    polygon=keck_i_altaz_polygon_restriction,
    altitude_min=keck_i_alt_min,
    altitude_max=keck_i_alt_max,
)

keck_ii_altaz_polygon_restriction = Polygon(
    [
        [18.0, 185.3],
        [36.8, 185.3],
        [36.8, 332.8],
        [18.0, 332.8],
        [18.0, 185.3],
    ]
)

keck_ii_alt_min = 18.0
keck_ii_alt_max = 89.5

KECK_II_ALTAZ_CONSTRAINT = AltAzConstraint(
    polygon=keck_ii_altaz_polygon_restriction,
    altitude_min=keck_ii_alt_min,
    altitude_max=keck_ii_alt_max,
)

OBSERVATORY: dict = {
    "id": uuid.UUID("eeab0ee9-a6b7-4d4d-ae95-8717e2817063"),
    "name": "W. M. Keck Observatory",
    "short_name": "Keck",
    "type": ObservatoryType.GROUND_BASED.value,
    "operational_begin_date": datetime(1993, 5, 1, 0, 0, 0),
    "reference_url": "https://keckobservatory.org",
    "telescopes": [
        {
            "id": uuid.UUID("bb811891-76d6-476d-9141-430c6ef5830d"),
            "name": "Keck I",
            "short_name": "Keck I",
            "is_operational": True,
            "reference_url": "https://keckobservatory.org/our-story/telescopes/",
            "instruments": [
                {
                    "id": uuid.UUID("1cebeac0-625e-4477-9583-2e4166d4a0d7"),
                    "name": "High Resolution Echelle Spectrometer",
                    "short_name": "HIRES",
                    "type": InstrumentType.SPECTROSCOPIC_HIGH_RES.value,
                    "field_of_view": InstrumentFOV.POINT.value,
                    "footprint": [],
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/hires/",
                    "filters": [
                        {
                            "id": uuid.UUID("5b7bdaa6-b435-4424-b880-a9a7c338ecfd"),
                            "name": "HIRES Bandpass",
                            "min_wavelength": HIRES_BANDPASS.min,
                            "max_wavelength": HIRES_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                },
                {
                    "id": uuid.UUID("8dbb846c-c472-41db-96cb-68ddde1a1623"),
                    "name": "Low-Resolution Imaging Spectrograph",
                    "short_name": "LRIS",
                    # LRIS is a photometer, multi-object spectrograph, and polarimeter
                    # but for now let's just say it's a low-resolution spectrograph
                    "type": InstrumentType.SPECTROSCOPIC_LOW_RES.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": LRIS_FOOTPRINT,
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/lris/",
                    "filters": [
                        {
                            "id": uuid.UUID("542acde6-e84b-4dad-b394-c98209342bc6"),
                            "name": "LRIS Bandpass",
                            "min_wavelength": LRIS_BANDPASS.min,
                            "max_wavelength": LRIS_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("9d5b016c-b7bd-4a75-939e-1f8193cf3a9c"),
                            "name": "LRIS u'",
                            "min_wavelength": LRIS_U_BANDPASS.min,
                            "max_wavelength": LRIS_U_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("b91bc90a-0c00-48b1-8802-fc33d43fe14e"),
                            "name": "LRIS B",
                            "min_wavelength": LRIS_B_BANDPASS.min,
                            "max_wavelength": LRIS_B_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("e3e4e09b-2d43-4b8a-9f04-68e6918362a1"),
                            "name": "LRIS g",
                            "min_wavelength": LRIS_G_BANDPASS.min,
                            "max_wavelength": LRIS_G_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("aad1dfd3-de7b-4fef-ac9d-61858f7aef79"),
                            "name": "LRIS V",
                            "min_wavelength": LRIS_V_BANDPASS.min,
                            "max_wavelength": LRIS_V_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("f360e9fc-c1b3-405f-bcb9-bb909a24c205"),
                            "name": "LRIS R",
                            "min_wavelength": LRIS_R_BANDPASS.min,
                            "max_wavelength": LRIS_R_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("a656f058-c727-4132-96e7-2fb837d9d16f"),
                            "name": "LRIS Rs",
                            "min_wavelength": LRIS_RS_BANDPASS.min,
                            "max_wavelength": LRIS_RS_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("60a58bf4-926d-4501-9e88-1fd5ef58df15"),
                            "name": "LRIS I",
                            "min_wavelength": LRIS_I_BANDPASS.min,
                            "max_wavelength": LRIS_I_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("9e9002ad-6978-48ae-82d3-bafc22036b1f"),
                    "name": "Keck Planet Finder",
                    "short_name": "KPF",
                    "type": InstrumentType.SPECTROSCOPIC_HIGH_RES.value,
                    "field_of_view": InstrumentFOV.POINT.value,
                    "footprint": [],
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/keck-planet-finder/",
                    "filters": [
                        {
                            "id": uuid.UUID("b0ea8eb1-b012-4316-b0a1-9ee657209e8f"),
                            "name": "KPF Bandpass",
                            "min_wavelength": KPF_BANDPASS.min,
                            "max_wavelength": KPF_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("c918760f-266b-475c-99b0-76610c0e1e10"),
                    "name": "Multi-Object Spectrograph for Infrared Exploration",
                    "short_name": "MOSFIRE",
                    # MOSFIRE is a multi-object imaging spectrograph
                    "type": InstrumentType.SPECTROSCOPIC_LOW_RES.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": MOSFIRE_FOOTPRINT,
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/mosfire/",
                    "filters": [
                        {
                            "id": uuid.UUID("1a651178-5023-4d3c-b9b5-8a7ba4bb6388"),
                            "name": "MOSFIRE Y",
                            "min_wavelength": MOSFIRE_Y_BANDPASS.min,
                            "max_wavelength": MOSFIRE_Y_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("d744f1f1-ea8c-419f-8c49-1f84750d6f38"),
                            "name": "MOSFIRE J",
                            "min_wavelength": MOSFIRE_J_BANDPASS.min,
                            "max_wavelength": MOSFIRE_J_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("e9858a7c-4e92-48a1-b99f-b7b47ebf8ab2"),
                            "name": "MOSFIRE H",
                            "min_wavelength": MOSFIRE_H_BANDPASS.min,
                            "max_wavelength": MOSFIRE_H_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("aa9c625e-a8fa-49d6-bdbc-792b27eb6e9f"),
                            "name": "MOSFIRE K",
                            "min_wavelength": MOSFIRE_K_BANDPASS.min,
                            "max_wavelength": MOSFIRE_K_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
            ],
            "constraints": [
                {
                    "id": uuid.UUID("daae8f0c-f59a-4915-ae85-ebb7cbba48e0"),
                    "constraint_type": ConstraintType.ALT_AZ,
                    "constraint_parameters": KECK_I_ALTAZ_CONSTRAINT.model_dump(),
                }
            ],
        },
        {
            "id": uuid.UUID("74c41e48-5428-4c7a-a16c-6e47e2a7a484"),
            "name": "Keck II",
            "short_name": "Keck II",
            "is_operational": True,
            "reference_url": "https://keckobservatory.org/our-story/telescopes/",
            "instruments": [
                {
                    "id": uuid.UUID("600b3804-72f8-45ba-a865-512390d01eb1"),
                    "name": "Near-infrared Camera, Second Generation",
                    "short_name": "NIRC2",
                    # NIRC2 is a NIR imager and spectrograph,
                    # but for now let's just call it an imager
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": NIRC2_FOOTPRINT,
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/nirc2/",
                    "filters": [
                        {
                            "id": uuid.UUID("c171dcb9-0080-4183-8532-dd0c5ed628db"),
                            "name": "NIRC2 z",
                            "min_wavelength": NIRC2_Z_BANDPASS.min,
                            "max_wavelength": NIRC2_Z_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("f56ba7ca-7a9c-49ef-b0ea-e239a7760793"),
                            "name": "NIRC2 Y",
                            "min_wavelength": NIRC2_Y_BANDPASS.min,
                            "max_wavelength": NIRC2_Y_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("ff20163a-c57d-48f2-9b97-16f1b5c894cd"),
                            "name": "NIRC2 J",
                            "min_wavelength": NIRC2_J_BANDPASS.min,
                            "max_wavelength": NIRC2_J_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("7936ed37-d95c-4a04-9aab-58e3482b918e"),
                            "name": "NIRC2 H",
                            "min_wavelength": NIRC2_H_BANDPASS.min,
                            "max_wavelength": NIRC2_H_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("2eabb5fe-1ff8-4be9-8801-c3d62fbbe613"),
                            "name": "NIRC2 K",
                            "min_wavelength": NIRC2_K_BANDPASS.min,
                            "max_wavelength": NIRC2_K_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("6ca77fa8-843d-4817-80d2-c67a615f6fd6"),
                            "name": "NIRC2 Ks",
                            "min_wavelength": NIRC2_KS_BANDPASS.min,
                            "max_wavelength": NIRC2_KS_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("b5b890e6-8028-4d48-a76b-b6706d8ead56"),
                            "name": "NIRC2 Kp",
                            "min_wavelength": NIRC2_KP_BANDPASS.min,
                            "max_wavelength": NIRC2_KP_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("eab2a043-aec7-45ff-8bad-970b0b6d09bf"),
                            "name": "NIRC2 Lw",
                            "min_wavelength": NIRC2_LW_BANDPASS.min,
                            "max_wavelength": NIRC2_LW_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("78539254-82b3-4fb6-8587-f272ee6e569d"),
                            "name": "NIRC2 Lp",
                            "min_wavelength": NIRC2_LP_BANDPASS.min,
                            "max_wavelength": NIRC2_LP_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("5d5b66e8-cc5e-4784-bda3-0962b24249c7"),
                            "name": "NIRC2 Ms",
                            "min_wavelength": NIRC2_MS_BANDPASS.min,
                            "max_wavelength": NIRC2_MS_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("090fda08-f882-46ba-a403-107156f57ecd"),
                    "name": "Near Infrared Spectrometer",
                    "short_name": "NIRSPEC",
                    "type": InstrumentType.SPECTROSCOPIC_HIGH_RES.value,
                    "field_of_view": InstrumentFOV.POINT.value,
                    "footprint": [],
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/nirspec/",
                    "filters": [
                        {
                            "id": uuid.UUID("d27bafd2-e2d9-46b0-85ca-054b93b27e78"),
                            "name": "NIRSPEC Bandpass",
                            "min_wavelength": NIRSPEC_BANDPASS.min,
                            "max_wavelength": NIRSPEC_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                },
                {
                    "id": uuid.UUID("d511af8e-5d11-4339-b63c-cd6489840ce8"),
                    "name": "Echellette Spectrograph and Imager",
                    "short_name": "ESI",
                    # ESI is both an imager and spectrograph,
                    # but it's primarily used as a spectrograph
                    "type": InstrumentType.SPECTROSCOPIC_LOW_RES.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": ESI_FOOTPRINT,
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/esi/",
                    "filters": [
                        {
                            "id": uuid.UUID("964b05ec-4039-4e45-89cb-dbdb85fae591"),
                            "name": "ESI Bandpass",
                            "min_wavelength": ESI_BANDPASS.min,
                            "max_wavelength": ESI_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("46427e64-00c6-4c98-ae48-7b27016f535c"),
                            "name": "ESI B",
                            "min_wavelength": ESI_B_BANDPASS.min,
                            "max_wavelength": ESI_B_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("ccd8a00a-ce45-4666-a81f-44bc3d5b4bd6"),
                            "name": "ESI V",
                            "min_wavelength": ESI_V_BANDPASS.min,
                            "max_wavelength": ESI_V_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("ea87fe4d-ba2d-465b-8c52-78c0271b73bd"),
                            "name": "ESI R",
                            "min_wavelength": ESI_R_BANDPASS.min,
                            "max_wavelength": ESI_R_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("bac78d2d-2817-4d34-b55e-6f67613a61f6"),
                    "name": "Deep Extragalactic Imaging Multi-Object Spectrograph",
                    "short_name": "DEIMOS",
                    # DEIMOS is a multi-object spectrograph and imager
                    "type": InstrumentType.SPECTROSCOPIC_HIGH_RES.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": DEIMOS_FOOTPRINT,
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/deimos/",
                    "filters": [
                        {
                            "id": uuid.UUID("f70aa52d-d6da-4dc2-b23a-d2db5bb48105"),
                            "name": "DEIMOS Bandpass",
                            "min_wavelength": DEIMOS_BANDPASS.min,
                            "max_wavelength": DEIMOS_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("703c0b55-08a0-4a99-b9e6-dc0b13c6e557"),
                            "name": "DEIMOS B",
                            "min_wavelength": DEIMOS_B_BANDPASS.min,
                            "max_wavelength": DEIMOS_B_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("434fa960-db24-4271-9238-4010fe181c62"),
                            "name": "DEIMOS V",
                            "min_wavelength": DEIMOS_V_BANDPASS.min,
                            "max_wavelength": DEIMOS_V_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("8282aedc-08e3-4bb4-8098-6b99a5e5de62"),
                            "name": "DEIMOS R",
                            "min_wavelength": DEIMOS_R_BANDPASS.min,
                            "max_wavelength": DEIMOS_R_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("2e835669-c863-444a-9e99-cc7a13466c92"),
                            "name": "DEIMOS I",
                            "min_wavelength": DEIMOS_I_BANDPASS.min,
                            "max_wavelength": DEIMOS_I_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("61acb4d3-d985-4f9f-a479-94d8797fc1a7"),
                            "name": "DEIMOS Z",
                            "min_wavelength": DEIMOS_Z_BANDPASS.min,
                            "max_wavelength": DEIMOS_Z_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("9b70dd96-b210-4aca-8d16-08e9163e2fb9"),
                    "name": "Keck Cosmic Web Imager",
                    "short_name": "KCWI",
                    # KCWI is an IFU spectrograph, but let's call it a spectrograph for now
                    "type": InstrumentType.SPECTROSCOPIC_LOW_RES.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": KCWI_FOOTPRINT,
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/kcwi/",
                    "filters": [
                        {
                            "id": uuid.UUID("147fbc00-6365-4b75-889f-45f462e4566c"),
                            "name": "KCWI Bandpass",
                            "min_wavelength": KCWI_BANDPASS.min,
                            "max_wavelength": KCWI_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("ae8d23e3-df02-4657-b593-854aba2003fc"),
                    "name": "Near Infrared Echellette Spectrograph",
                    "short_name": "NIRES",
                    "type": InstrumentType.SPECTROSCOPIC_LOW_RES.value,
                    "field_of_view": InstrumentFOV.POINT.value,
                    "footprint": [],
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "reference_url": "https://keckobservatory.org/our-story/telescopes/nires/",
                    "filters": [
                        {
                            "id": uuid.UUID("acf634cb-f29f-45bc-8409-9241d01d4843"),
                            "name": "NIRES Bandpass",
                            "min_wavelength": NIRES_BANDPASS.min,
                            "max_wavelength": NIRES_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
            ],
            "constraints": [
                {
                    "id": uuid.UUID("073ce27e-82fd-481b-a471-af09b135ee96"),
                    "constraint_type": ConstraintType.ALT_AZ,
                    "constraint_parameters": KECK_II_ALTAZ_CONSTRAINT.model_dump(),
                }
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("c214779d-536d-415b-a662-dc99ff498434"),
            "ephemeris_type": EphemerisType.GROUND,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("7f4f80db-b50e-4673-bd9f-bd86c997d391"),
                "latitude": 19.82636,
                "longitude": -155.47501,
                "height": 4123,
            },
        },
    ],
    "group": {
        "id": uuid.UUID("ddc5464a-1c7b-4560-9800-83fe04807fd6"),
        "name": "Keck Observatory",
        "short_name": "Keck",
        "group_admin": {
            "id": uuid.UUID("ac69c65f-716f-43b3-b503-9df12c084bf4"),
            "name": "Keck Group Admin",
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
