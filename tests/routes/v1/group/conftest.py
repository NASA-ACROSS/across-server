# from uuid import UUID, uuid4

# import pytest

# from across_server.db import models


# @pytest.fixture
# def fake_group_data(fake_group_role: models.GroupRole) -> models.Group:
#     return models.Group(
#         **{
#             "id": str(uuid4()),
#             "name": "test group",
#             "roles": [fake_group_role],
#             "users": [],  # gets populated with mock_user_data at runtime by the model because of groups relationship in mock_user_data below
#         }
#     )
