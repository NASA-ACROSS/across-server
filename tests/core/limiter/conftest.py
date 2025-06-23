from typing import Any, MutableMapping

import pytest


@pytest.fixture(scope="function")
def mock_scope() -> MutableMapping[str, Any]:
    return {
        "client": ("13.13.13.13", "1234"),
        "headers": [
            (
                b"authorization",
                b"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMmM4MzRhNC0yMzJjLTQyMGEtOTg1ZS1lYjViYzU5YWJhMjQiLCJleHAiOjE3NTA3ODIxNjgsInNjb3BlcyI6W10sImdyb3VwcyI6W3siaWQiOiI4MWVhN2FjMS1kYTA3LTQ5ZTMtYjFiNy1mYjA4YjYwMzRjMTUiLCJzY29wZXMiOlsiZ3JvdXA6d3JpdGUiLCJncm91cDpzY2hlZHVsZTp3cml0ZSIsImdyb3VwOnJlYWQiLCJncm91cDpvYnNlcnZhdG9yeTp3cml0ZSIsImdyb3VwOnJvbGU6d3JpdGUiLCJncm91cDp1c2VyOndyaXRlIiwiZ3JvdXA6dGVsZXNjb3BlOndyaXRlIl19XSwidHlwZSI6InVzZXIifQ.cT9Qm0Grvdv1vfzgkNZzLrC845z_dRfvaPIh00P10IA",
            )
        ],
    }
