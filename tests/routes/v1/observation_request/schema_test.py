import pytest

from across_server.routes.v1.observation_request import schemas as obs_req_schemas


class TestObservationRequestCreateSchema:
    @pytest.mark.asyncio
    async def test_should_throw_value_error_when_observation_window_end_less_than_or_equal_to_begin(
        self, fake_observation_request_json: dict
    ) -> None:
        """Should throw value error when date range end <= begin"""
        fake_observation_request_json["observation_window"]["end"] = (
            fake_observation_request_json["observation_window"]["begin"]
        )
        with pytest.raises(ValueError):
            obs_req_schemas.ObservationRequestCreate.model_validate(
                fake_observation_request_json
            )

    @pytest.mark.asyncio
    async def test_should_pass_validation_when_observation_window_end_greater_than_begin(
        self, fake_observation_request_json: dict
    ) -> None:
        """Should pass validation when date range end > begin"""
        validated_schema = obs_req_schemas.ObservationRequestCreate.model_validate(
            fake_observation_request_json
        )

        assert isinstance(validated_schema, obs_req_schemas.ObservationRequestCreate)
