import uuid

from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums

### ACS WFC Filters

# [filter_name, central_wavelength, bandwidth, uuid]
# Reference: https://hst-docs.stsci.edu/acsihb/chapter-5-imaging/5-1-imaging-overview
ACS_WFC_FILTER_INFO: list[tuple[str, float, float, str]] = [
    ("CLEAR1L", 6200.0, 5200.0, "904f1562-81d8-4bcd-a5c6-0fc8aeba442a"),
    ("CLEAR2L", 6000.0, 5200.0, "016132f7-ff00-4220-90a2-41ce0b8d2d0d"),
    ("F555W", 5346.0, 1193.0, "998a6260-48c9-4dc4-95fe-ffa9d5cb0bc2"),
    ("F775W", 7764.0, 1528.0, "cf08026b-74fe-4e46-986e-e0866f889120"),
    ("F625W", 6318.0, 1442.0, "b7fa0177-bf24-4fff-b255-c83e92880774"),
    ("F550M", 5580.0, 547.0, "77540981-6795-46f5-b686-8809d6f9104e"),
    ("F850LP", 9445.0, 1229.0, "d29d781f-722e-4e84-a414-02f0de060b22"),
    ("F892N", 8917.0, 154.0, "b63ef0d4-aead-41e6-adde-7ed44a032b54"),
    ("F606W", 5907.0, 2342.0, "43bb2821-26cb-4e0f-ad10-8b74d4cc4683"),
    ("F502N", 5022.0, 57.0, "3ec6d252-9a59-40cd-b3b2-d8c07ab94772"),
    ("F658N", 6584.0, 78.0, "d70b0517-bdec-425d-bba0-4ee7b712f9c5"),
    ("F475W", 4760.0, 1458.0, "38c52de3-fef5-4101-b9ff-66fe86f1b30b"),
    ("F660N", 6602.0, 40.0, "d481f769-96f8-455e-8948-8c72ecbd530d"),
    ("F814W", 8333.0, 2511.0, "604bd2b1-72cc-4f5e-95eb-7bc78d607f39"),
    ("F435W", 4297.0, 1038.0, "5ab68eec-59eb-4eb2-9f56-61f77742466a"),
]

# [filter_name, min_wavelength, max_wavelength, uuid]
# Reference: https://hst-docs.stsci.edu/acsihb/chapter-5-imaging/5-1-imaging-overview
ACS_WFC_GRATING_RAMP_INFO: list[tuple[str, float, float, str]] = [
    ("G800L", 5800.0, 11000.0, "e2559a1c-5d08-430d-ba5d-ce74ddd905a2"),
    ("FR388N", 3710.0, 4050.0, "75b7902b-e2ad-493b-ad1b-c11b1aa6560c"),
    ("FR423N", 4050.0, 4420.0, "41a11075-adc2-4fba-8d5f-01fb68136020"),
    ("FR462N", 4420.0, 4820.0, "44e8c224-13f8-47c4-9bfe-448592d037c2"),
    ("FR656N", 6270.0, 6850.0, "8bdd5b51-6813-44de-b85e-ccd078481725"),
    ("FR716N", 6850.0, 7470.0, "788d3395-ee02-4f25-af40-efa44f4b873f"),
    ("FR782N", 7470.0, 8160.0, "262b6345-5107-4c47-b65f-75227f4b4b59"),
    ("FR914M", 7570.0, 10710.0, "3796763f-1c90-454e-99f0-e6aa21399984"),
    ("FR853N", 8160.0, 8910.0, "76ed1d5f-505e-423c-911b-931fde5d35d3"),
    ("FR931N", 8910.0, 9720.0, "b1260468-b6bd-484d-97e9-a196e309e46b"),
    ("FR459M", 3810.0, 5370.0, "26196c8d-f33b-4947-81e8-4da456276487"),
    ("FR647M", 5370.0, 7570.0, "f3a18242-4ebd-41a7-ae47-cc7da7d97502"),
    ("FR1016N", 9720.0, 10610, "b8d52d0e-b1bb-4ac7-9453-8eeaffae0516"),
    ("FR505N", 4820.0, 5270.0, "4f60c7e2-fdf4-4e07-b0c8-eeaa623a817f"),
    ("FR551N", 5270.0, 5750.0, "09f75efb-97ac-4043-a2f7-a58e6887ef78"),
    ("FR601N", 5750.0, 6270.0, "9d7309ee-fcd0-42dd-a3e1-0673fee50f28"),
]

ACS_WFC_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        central_wavelength=filt[1],
        bandwidth=filt[2],
        unit=tools_enums.WavelengthUnit.ANGSTROM,
    )
    for filt in ACS_WFC_FILTER_INFO
]

ACS_WFC_GRATING_RAMP_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        min=filt[1],
        max=filt[2],
        unit=tools_enums.WavelengthUnit.ANGSTROM,
    )
    for filt in ACS_WFC_GRATING_RAMP_INFO
]

ACS_WFC_FILTERS: list[dict] = [
    {
        "id": uuid.UUID(ACS_WFC_FILTER_INFO[i][-1]),
        "name": "HST ACS WFC " + ACS_WFC_FILTER_INFO[i][0],
        "min_wavelength": bandpass.min,
        "max_wavelength": bandpass.max,
        "is_operational": True,
        "reference_url": "https://hst-docs.stsci.edu/acsihb/chapter-5-imaging/5-1-imaging-overview",
    }
    for i, bandpass in enumerate(ACS_WFC_BANDPASSES)
] + [
    {
        "id": uuid.UUID(ACS_WFC_GRATING_RAMP_INFO[i][-1]),
        "name": "HST ACS WFC " + ACS_WFC_GRATING_RAMP_INFO[i][0],
        "min_wavelength": bandpass.min,
        "max_wavelength": bandpass.max,
        "is_operational": True,
        "reference_url": "https://hst-docs.stsci.edu/acsihb/chapter-5-imaging/5-1-imaging-overview",
    }
    for i, bandpass in enumerate(ACS_WFC_GRATING_RAMP_BANDPASSES)
]


### WFC3 UVIS Filters
# [filter_name, central_wavelength, bandwidth, uuid]
# Reference: https://hst-docs.stsci.edu/wfc3ihb/chapter-6-uvis-imaging-with-wfc3/6-5-uvis-spectral-elements
WFC3_UVIS_FILTER_INFO: list[tuple[str, float, float, str]] = [
    ("F200LP", 4971.9, 5881.1, "6975cf5c-af95-4343-8f72-843a59db2ea0"),
    ("F300X", 2820.5, 707.3, "2607ce13-2c51-40dc-88af-e34afc111981"),
    ("F350LP", 5873.9, 4803.7, "de1cf0d1-a7f1-4886-99c3-498ad7fe45b1"),
    ("F475X", 4940.7, 2057.2, "cbbd1698-8226-4487-8a40-ef7763359922"),
    ("F600LP", 7468.1, 2340.1, "f260ce32-f2be-45d0-9080-e0a2c713f60f"),
    ("F850LP", 9176.1, 1192.5, "490fdc1e-440e-4a76-991b-4659ea3db843"),
    ("F218W", 2228, 330.7, "1c8894c8-a8be-4d49-9fe6-f7c9267f68ba"),
    ("F225W", 2372.1, 467.1, "083ba989-9a67-42f9-bd29-58eabec7871c"),
    ("F275W", 2709.7, 405.3, "f499c9d8-581a-4ad8-ad2d-7c819bfe771c"),
    ("F336W", 3354.5, 511.6, "a2fd052b-570c-47da-a9a8-0b3eb00bb62f"),
    ("F390W", 3923.7, 894.0, "670e10ce-07dc-47f2-abb9-f13af6949380"),
    ("F438W", 4326.2, 614.7, "907344d1-2d7a-4647-85cf-b65efd75fb75"),
    ("F475W", 4773.1, 1343.5, "7803ff78-b24a-4b68-98d8-c03ee56c38fb"),
    ("F555W", 5308.4, 1565.4, "7bbc9d83-ab14-4cd8-891b-ad2dcbb6ab5d"),
    ("F606W", 5889.2, 2189.2, "d4d24c66-f6fb-4e5e-8eef-cbbb80829209"),
    ("F625W", 6242.6, 1464.6, "7ae40983-2ec5-4fb2-9696-09621edd20b3"),
    ("F775W", 7651.4, 1179.1, "4cf8a347-9111-4ce8-b75a-d8d308461396"),
    ("F814W", 8039.1, 1565.2, "c174098e-a06b-49ae-a848-dc00882cc329"),
    ("F390M", 3897.2, 204.3, "963ba1d7-4f85-415c-9113-a06c40478a35"),
    ("F410M", 4109.0, 172.0, "5f20e7bf-ee85-4eb1-b058-cf7abc01ec63"),
    ("FQ422M", 4219.2, 111.7, "4d640c14-1399-43e4-9880-231086247ac9"),
    ("F467M", 4682.6, 200.9, "a5c2fc58-c9c6-47a0-be5c-823303d8e23d"),
    ("F547M", 5447.5, 650.0, "9b6f237f-5c03-4cde-b65f-670e607e1f4d"),
    ("F621M", 6218.9, 609.5, "5d489ad7-0807-447b-b863-c50ee0e6c6db"),
    ("F689M", 6876.8, 684.2, "289da048-74b3-4e2f-8144-0131a940a1f5"),
    ("F763M", 7614.4, 708.6, "c795d811-12a0-4d44-93ac-5ab0ca6518ae"),
    ("F845M", 8439.1, 794.3, "1c4ec315-151a-4423-a11b-5563fe79d7ba"),
    ("FQ232N", 2432.2, 34.2, "fabf3400-de17-4570-a8ef-40cc67a1844c"),
    ("FQ243N", 2476.3, 36.7, "aade2b33-7a1a-4b65-81b7-7f1c9a31c9e6"),
    ("F280N", 2832.9, 42.5, "0a33982c-ff17-4565-955a-8db94d5310a2"),
    ("F343N", 3435.1, 249.1, "7e8eb762-3e48-478a-aa76-8c6319243b09"),
    ("F373N", 3730.2, 49.6, "0c70b113-df45-4386-8a31-b17e1e1ad0b8"),
    ("FQ378N", 3792.4, 99.3, "7d32eba8-dc6e-4b46-a80e-9c34d7858eee"),
    ("FQ387N", 3873.7, 33.6, "80e0a395-9d96-4021-bd4d-68684f0f4f6f"),
    ("F395N", 3955.2, 85.2, "44278da9-d08b-4753-8793-1a06d4defa23"),
    ("FQ436N", 4367.2, 43.4, "d4dcd09d-3d71-4ec9-bd67-66ea10d9b84a"),
    ("FQ437N", 4371.0, 30.0, "75679391-1a04-43aa-b990-fd079e173df8"),
    ("F469N", 4688.1, 49.7, "c5793244-2922-41fb-9d2a-255d90e2b512"),
    ("F487N", 4871.4, 60.4, "e1641730-d7bb-4123-836b-15aa151b35fd"),
    ("FQ492N", 4933.4, 113.5, "3eb679b5-7ff5-4f0e-b512-d7e4ef38d44d"),
    ("F502N", 5009.6, 65.3, "5b301da4-296a-4185-8916-dfd98d978f4b"),
    ("FQ508N", 5091, 130.6, "3dce5f71-0f5c-4875-b0bc-4da110591206"),
    ("FQ575N", 5757.7, 18.4, "a5234556-3d08-4455-bcde-fe65e4ffe64e"),
    ("FQ619N", 6198.5, 60.9, "2c3e1f3e-e969-491c-8e6a-a9e9d14a9282"),
    ("F631N", 6304.3, 58.3, "5c3be579-540d-444f-9b68-22e1e380a41e"),
    ("FQ634N", 6349.2, 64.1, "fe9fb59d-6870-497a-b320-3f27f0917b68"),
    ("F645N", 6453.6, 84.2, "cb6cf47f-96ef-4a18-87b3-959ccaf85e11"),
    ("F656N", 6561.4, 17.6, "2102d6be-99dd-4343-855d-8bcf37b226a8"),
    ("F657N", 6566.6, 121.0, "f726f11b-e7fd-4e42-9fdd-bb9dc542c7e3"),
    ("F658N", 6584, 27.6, "c1dae66e-31fe-4746-b8b1-1c10fcc75960"),
    ("F665N", 6655.9, 131.3, "c0198aa5-f9e2-4778-b087-afea3c78a307"),
    ("FQ672N", 6716.4, 19.4, "55241336-2df5-4e7d-a72c-b88aae7eff51"),
    ("F673N", 6765.9, 117.8, "edff27d7-22bb-4ad3-a779-5d95a58c5b31"),
    ("FQ674N", 6730.7, 17.6, "d8c4a03f-eb0d-492b-b8a1-9c776e5dd5b3"),
    ("F680N", 6877.6, 370.5, "fd1868cd-1f38-4867-8770-b242276138d0"),
    ("FQ727N", 7275.2, 63.9, "47d113a7-525a-414a-90a4-1a04b41aa437"),
    ("FQ750N", 7502.5, 70.4, "1c18b3fe-084a-4632-8cb0-bedaf760acee"),
    ("FQ889N", 8892.2, 98.5, "ee46764b-d6cc-406b-8c44-d4f58034ce96"),
    ("FQ906N", 9057.8, 98.6, "0261ee73-72f4-4951-b281-f126cfa299e6"),
    ("FQ924N", 9247.6, 91.6, "0e1120f7-078b-457e-8059-f33f6d62166a"),
    ("FQ937N", 9372.4, 93.3, "71d6903c-7569-46e5-8a04-ef01171a014f"),
    ("F953N", 9530.6, 96.8, "a49571dd-d6c1-4a64-9039-6eaf4c5db7b1"),
]

# [filter_name, min_wavelength, max_wavelength, uuid]
# Reference: https://hst-docs.stsci.edu/wfc3ihb/chapter-6-uvis-imaging-with-wfc3/6-5-uvis-spectral-elements
WFC3_UVIS_GRATING_INFO: list[tuple[str, float, float, str]] = [
    ("G2806", 2000.0, 8000.0, "9dd17db7-9a11-4d8e-86bc-cc21c1d138dd")
]

WFC3_UVIS_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        central_wavelength=filt[1],
        bandwidth=filt[2],
        unit=tools_enums.WavelengthUnit.ANGSTROM,
    )
    for filt in WFC3_UVIS_FILTER_INFO
]

WFC3_UVIS_GRATING_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        min=filt[1],
        max=filt[2],
        unit=tools_enums.WavelengthUnit.ANGSTROM,
    )
    for filt in WFC3_UVIS_GRATING_INFO
]

WFC3_UVIS_FILTERS: list[dict] = [
    {
        "id": uuid.UUID(WFC3_UVIS_FILTER_INFO[i][-1]),
        "name": "HST WFC3 " + WFC3_UVIS_FILTER_INFO[i][0],
        "min_wavelength": bandpass.min,
        "max_wavelength": bandpass.max,
        "is_operational": True,
        "reference_url": "https://hst-docs.stsci.edu/wfc3ihb/chapter-6-uvis-imaging-with-wfc3/6-5-uvis-spectral-elements",
    }
    for i, bandpass in enumerate(WFC3_UVIS_BANDPASSES)
] + [
    {
        "id": uuid.UUID(WFC3_UVIS_GRATING_INFO[i][-1]),
        "name": "HST WFC3 " + WFC3_UVIS_GRATING_INFO[i][0],
        "min_wavelength": bandpass.min,
        "max_wavelength": bandpass.max,
        "is_operational": True,
        "reference_url": "https://hst-docs.stsci.edu/acsihb/chapter-5-imaging/5-1-imaging-overview",
    }
    for i, bandpass in enumerate(WFC3_UVIS_GRATING_BANDPASSES)
]


### WFC3 IR Filters
# [filter_name, central_wavelength, bandwidth, uuid] (in nanometers)
# Reference: https://hst-docs.stsci.edu/wfc3ihb/chapter-7-ir-imaging-with-wfc3/7-5-ir-spectral-elements
WFC3_IR_FILTER_INFO: list[tuple[str, float, float, str]] = [
    ("F105W", 1055.2, 265.0, "c477802d-fc20-4a50-999c-ee12a706d0b5"),
    ("F110W", 1153.4, 443.0, "2cc1254d-25c5-4c76-8040-7999dffbcd4d"),
    ("F125W", 1248.6, 284.5, "87e04f8f-cb01-4f06-b6e9-24eedb0d0f41"),
    ("F140W", 1392.3, 384.0, "9e830839-c1aa-4bfe-a8f1-d1d0fb115605"),
    ("F160W", 1536.9, 268.3, "0dad716a-6b14-40c8-a777-d4c0840c2909"),
    ("F098M", 986.4, 157.0, "b0c5cb13-459a-4754-8e3b-dcb2c4a306e2"),
    ("F127M", 1274.0, 68.8, "0d24940a-2d79-4c9c-8100-805fcac672db"),
    ("F139M", 1383.8, 64.3, "5dd6689d-8981-4a42-8451-9c381eda6ac5"),
    ("F153M", 1532.2, 68.5, "a216c7ea-8cce-4c23-8a71-080cede413ce"),
    ("F126N", 1258.5, 15.2, "e577b2c4-4d1e-44cb-8e5b-8e14c2f3d2de"),
    ("F128N", 1283.2, 15.9, "72a559fb-9470-4bd5-bfc1-5a23a6838397"),
    ("F130N", 1300.6, 15.6, "5e01c647-41b4-4d27-ba19-f77f6847a6ad"),
    ("F132N", 1318.8, 16.1, "6550f01e-02f0-4645-b7f6-7cc8e66034a1"),
    ("F164N", 1640.4, 20.9, "285905a8-8261-410b-b0d5-550903084087"),
    ("F167N", 1664.2, 21.0, "1ced011b-3058-440e-9715-03e280ebce18"),
]

# [filter_name, min_wavelength, max_wavelength, uuid] (in nanometers)
# # Reference: https://hst-docs.stsci.edu/wfc3ihb/chapter-7-ir-imaging-with-wfc3/7-5-ir-spectral-elements
WFC3_IR_GRATING_INFO: list[tuple[str, float, float, str]] = [
    ("G102", 800.0, 1150.0, "8eb86e1e-acf7-4da2-9fc0-b2b1b5a7d3f6"),
    ("G141", 1075.0, 1700.0, "a376847a-1bf9-496a-aa91-6fc527de46f4"),
]


WFC3_IR_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        central_wavelength=filt[1],
        bandwidth=filt[2],
        unit=tools_enums.WavelengthUnit.NANOMETER,
    )
    for filt in WFC3_IR_FILTER_INFO
]

WFC3_IR_GRATING_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        min=filt[1],
        max=filt[2],
        unit=tools_enums.WavelengthUnit.NANOMETER,
    )
    for filt in WFC3_IR_GRATING_INFO
]

WFC3_IR_FILTERS: list[dict] = [
    {
        "id": uuid.UUID(WFC3_IR_FILTER_INFO[i][-1]),
        "name": "HST WFC3 " + WFC3_IR_FILTER_INFO[i][0],
        "min_wavelength": bandpass.min,
        "max_wavelength": bandpass.max,
        "is_operational": True,
        "reference_url": "https://hst-docs.stsci.edu/wfc3ihb/chapter-7-ir-imaging-with-wfc3/7-5-ir-spectral-elements",
    }
    for i, bandpass in enumerate(WFC3_IR_BANDPASSES)
] + [
    {
        "id": uuid.UUID(WFC3_IR_GRATING_INFO[i][-1]),
        "name": "HST WFC3 " + WFC3_IR_GRATING_INFO[i][0],
        "min_wavelength": bandpass.min,
        "max_wavelength": bandpass.max,
        "is_operational": True,
        "reference_url": "https://hst-docs.stsci.edu/wfc3ihb/chapter-7-ir-imaging-with-wfc3/7-5-ir-spectral-elements",
    }
    for i, bandpass in enumerate(WFC3_IR_GRATING_BANDPASSES)
]


### COS Filters
# [filter_name, min_wavelength, max_wavelength, uuid]
# Reference: https://hst-docs.stsci.edu/cosihb/chapter-5-spectroscopy-with-cos/5-1-the-capabilities-of-cos
COS_GRATING_INFO: list[tuple[str, float, float, str]] = [
    ("G130M", 900.0, 1450.0, "59d7064d-2048-433f-9983-5292e6144b35"),
    ("G160M", 1360.0, 1775.0, "101c967b-3338-4b6f-a7d2-69dfb632e710"),
    ("G140L", 900.0, 2150.0, "08bec79c-d26f-447c-a6ae-de0f285f4ed7"),
    ("G185M", 1700.0, 2100.0, "91435e72-c35f-43b8-85aa-08843795addc"),
    ("G225M", 2100.0, 2500.0, "4b25132d-d5c2-4be2-844f-53ab9afb713b"),
    ("G285M5", 2500.0, 3200.0, "7e16e17d-fb7e-41a0-93be-16b49c13c581"),
    ("G230L", 1650.0, 3200.0, "cf4439ad-8263-4d0d-a228-8f80fb0a5450"),
]

COS_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        min=filt[1],
        max=filt[2],
        unit=tools_enums.WavelengthUnit.ANGSTROM,
    )
    for filt in COS_GRATING_INFO
]

COS_FILTERS: list[dict] = [
    {
        "id": uuid.UUID(COS_GRATING_INFO[i][-1]),
        "name": "HST COS " + COS_GRATING_INFO[i][0],
        "min_wavelength": bandpass.min,
        "max_wavelength": bandpass.max,
        "is_operational": True,
        "reference_url": "https://hst-docs.stsci.edu/cosihb/chapter-5-spectroscopy-with-cos/5-1-the-capabilities-of-cos",
    }
    for i, bandpass in enumerate(COS_BANDPASSES)
]


### STIS Filters

# [filter_name, min_wavelength, max_wavelength, uuid]
# Reference: https://hst-docs.stsci.edu/stisihb/chapter-4-spectroscopy/4-1-overview
STIS_GRATING_INFO: list[tuple[str, float, float, str]] = [
    ("G140L", 1150.0, 1730.0, "839eed42-6c11-4bcb-9711-6b86ea77a692"),
    ("G140M", 1140.0, 1740.0, "80fca90d-21b9-4331-b8ce-0f799073ee53"),
    ("G230L", 1570.0, 3180.0, "4fe8cf0f-c23b-40d2-8682-cbb04b767849"),
    ("G230M", 1640.0, 3100.0, "fabc8976-748f-4c23-aaec-23dfa5cb03e7"),
    ("G230LB", 1680.0, 3060.0, "6fb9948c-c004-4957-a410-d1784d4183d5"),
    ("G230MB", 1640.0, 3190.0, "467fa4eb-5888-444b-a85d-c45b462655d8"),
    ("G430L", 2900.0, 5700.0, "0b967023-30eb-401d-b7fd-69463f8cafb1"),
    ("G430M", 3020.0, 5610.0, "e75e664e-b999-4e74-9e32-9e65b67acc61"),
    ("G750L", 5240.0, 10270.0, "e7464395-6e34-4d60-9de2-bb483e679cf3"),
    ("G750M", 5450.0, 10140.0, "4d73daf5-fff6-4a7c-90b4-aeedf3d002b8"),
    ("E140M", 1144.0, 1710.0, "32bbdeae-0278-482d-b56f-5b22a676f352"),
    ("E140H", 1140.0, 1700.0, "6471bd24-5e1a-4cee-a51c-c1321e4abdca"),
    ("E230M", 1605.0, 3110.0, "fb5469ed-8562-4cef-a27c-5719b8e9e0de"),
    ("E230H", 1620.0, 3150.0, "751ad386-69dd-46b2-91bd-d9ba1143ebcc"),
    ("PRISM", 1150.0, 3620.0, "58fca2ca-a39c-4da9-be2e-509083f78aa3"),
]

# [filter_name, central_wavelength, bandwidth, uuid]
# Reference: https://hst-docs.stsci.edu/stisihb/chapter-5-imaging/5-1-imaging-overview
STIS_FILTER_INFO: list[tuple[str, float, float, str]] = [
    ("50CCD", 5852.0, 4410.0, "9302ec3b-781f-41a4-8026-13feb43ce447"),
    ("F28X50LP", 7229.0, 2722.0, "9a82a7d1-0cf5-4c96-b200-10c837487468"),
    ("F28X50OIII", 5006.0, 6.0, "b8f9ae15-cddd-43f7-8f38-00cc967cf2f1"),
    ("F28X50OII", 3737.0, 62.0, "75edb96b-938e-4a68-bdc7-4dd6876ab669"),
    ("50CORON", 5852.0, 4410.0, "ac4b3c9e-b629-4aea-bb0b-2d9fdde91427"),
    ("25MAMA-NUV", 2250.0, 1202.0, "ec19b034-7ca6-4bfc-8ff6-4793105f1dd6"),
    ("25MAMA-FUV", 1374.0, 324.0, "4f95cc90-78ae-458e-b828-c35400356d2c"),
    ("F25QTZ-NUV", 2365.0, 995.0, "623369fa-1ba9-4beb-b9c3-3829ddc271c5"),
    ("F25QTZ-FUV", 1595.0, 228.0, "314aec88-e5f7-461a-a9d6-e902866b45ee"),
    ("F25SRF2-NUV", 2299.0, 1128.0, "2cc8aab6-27d3-437f-9794-0a4cff04a32b"),
    ("F25SRF2-FUV", 1457.0, 284.0, "1e70c070-e89d-4805-b0ad-4d6657604870"),
    ("F25MGII", 2802.0, 45.0, "6e695ec8-c756-4a78-85ff-6ce8e95d7d7a"),
    ("F25CN270", 2709.0, 155.0, "83112b8f-b1ee-4279-bd1d-b983a5b87e27"),
    ("F25CIII", 1989.0, 173.0, "017a715a-edc6-4571-8a91-c6c3cb7f48eb"),
    ("F25CN182", 1981.0, 514.0, "6d55acc4-e6a1-4f52-b49a-e9a6c62084a1"),
    ("F25LYA", 1221.0, 72.0, "81488bea-c79e-4120-b486-6a96055226b3"),
]

# [filter_name, min_wavelength, max_wavelength, uuid]
# Reference: https://hst-docs.stsci.edu/stisihb/chapter-5-imaging/5-1-imaging-overview
STIS_NEUTRAL_DENSITY_FILTER_INFO: list[tuple[str, float, float, str]] = [
    ("F25NDQ1", 1150.0, 10300.0, "640b37c6-d37b-4fc3-a484-e6895f14f63e"),
    ("F25NDQ2", 1150.0, 10300.0, "f73cdc49-8cb7-41f1-984a-eeb7f8b7b129"),
    ("F25NDQ3", 1150.0, 10300.0, "3d7194e5-8a82-494a-9ef0-717675462ee5"),
    ("F25NDQ4", 1150.0, 10300.0, "27ebba1f-62ed-4b22-a82a-8bfa1246c221"),
    ("F25ND3", 1150.0, 10300.0, "fc8e36d5-8583-431a-bb05-4ad7a30c82c1"),
    ("F25ND5", 1150.0, 10300.0, "a2deba85-6318-4220-9bc9-4a131112ee92"),
]

STIS_GRATING_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        min=filt[1],
        max=filt[2],
        unit=tools_enums.WavelengthUnit.ANGSTROM,
    )
    for filt in STIS_GRATING_INFO
]

STIS_FILTER_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        central_wavelength=filt[1],
        bandwidth=filt[2],
        unit=tools_enums.WavelengthUnit.ANGSTROM,
    )
    for filt in STIS_FILTER_INFO
]

STIS_NEUTRAL_FILTER_BANDPASSES: list[WavelengthBandpass] = [
    WavelengthBandpass(
        filter_name=filt[0],
        min=filt[1],
        max=filt[2],
        unit=tools_enums.WavelengthUnit.ANGSTROM,
    )
    for filt in STIS_NEUTRAL_DENSITY_FILTER_INFO
]

STIS_FILTERS: list[dict] = (
    [
        {
            "id": uuid.UUID(STIS_GRATING_INFO[i][-1]),
            "name": "HST STIS " + STIS_GRATING_INFO[i][0],
            "min_wavelength": bandpass.min,
            "max_wavelength": bandpass.max,
            "is_operational": True,
            "reference_url": "https://hst-docs.stsci.edu/stisihb/chapter-4-spectroscopy/4-1-overview",
        }
        for i, bandpass in enumerate(STIS_GRATING_BANDPASSES)
    ]
    + [
        {
            "id": uuid.UUID(STIS_FILTER_INFO[i][-1]),
            "name": "HST STIS " + STIS_FILTER_INFO[i][0],
            "min_wavelength": bandpass.min,
            "max_wavelength": bandpass.max,
            "is_operational": True,
            "reference_url": "https://hst-docs.stsci.edu/stisihb/chapter-5-imaging/5-1-imaging-overview",
        }
        for i, bandpass in enumerate(STIS_FILTER_BANDPASSES)
    ]
    + [
        {
            "id": uuid.UUID(STIS_NEUTRAL_DENSITY_FILTER_INFO[i][-1]),
            "name": "HST STIS " + STIS_NEUTRAL_DENSITY_FILTER_INFO[i][0],
            "min_wavelength": bandpass.min,
            "max_wavelength": bandpass.max,
            "is_operational": True,
            "reference_url": "https://hst-docs.stsci.edu/stisihb/chapter-5-imaging/5-1-imaging-overview",
        }
        for i, bandpass in enumerate(STIS_NEUTRAL_FILTER_BANDPASSES)
    ]
)
