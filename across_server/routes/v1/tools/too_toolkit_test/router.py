from fastapi import APIRouter, status

router = APIRouter(
    prefix="/too_request",
    tags=["Tools"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The name resolver does not exist.",
        },
    },
)

dummy_test_configuration_data = {
    "testid": {
        "title": "Example ToO Request Page",
        "components": [
            {"type": "text", "name": "object_name", "label": "Object Name"},
            {"type": "number", "name": "exposure_time", "label": "Exposure Time"},
            {"type": "coordinate", "name": "target", "label": "Target Coordinates"},
            {
                "type": "select",
                "name": "instrument_mode",
                "label": "Instrument Mode",
                "placeholder": "Choose instrument mode",
                "options": [
                    {"label": "Imaging", "value": "imaging"},
                    {"label": "Spectroscopy", "value": "spectroscopy"},
                    {"label": "Polarimetry", "value": "polarimetry"},
                ],
            },
            {
                "type": "select",
                "name": "filters",
                "label": "Filters",
                "placeholder": "Choose filters",
                "options": [
                    {"label": "Filter A", "value": "filter_a"},
                    {"label": "Filter B", "value": "filter_b"},
                    {"label": "Filter C", "value": "filter_c"},
                ],
            },
            {
                "type": "select",
                "name": "urgency",
                "label": "Urgency",
                "placeholder": "Choose urgency level",
                "options": [
                    {"label": "Low", "value": "low"},
                    {"label": "Medium", "value": "medium"},
                    {"label": "High", "value": "high"},
                ],
            },
            {"type": "submit", "label": "Submit"},
        ],
    }
}


@router.get(
    "/{instrument_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a too request page configuration based on instrument name",
    description="Returns too request page configuration based on instrument name.",
    responses={
        status.HTTP_200_OK: {
            "description": "Return too request page configuration.",
        },
    },
)
async def too_toolkit_configuration(
    instrument_id: str,
) -> dict:
    return dummy_test_configuration_data.get(
        instrument_id, {"title": "Instrument Not Found", "components": []}
    )
