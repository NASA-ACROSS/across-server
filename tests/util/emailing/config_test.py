import os
import pytest
from across_server.util.email.config import Config
from unittest.mock import MagicMock



class TestEmailConfig:
    COMMON_CSV_TEST_CASES = [
        ("", []),
        (None, []),
        (",", []),
        (" , ", []),
        ("None", ["None"]),
        ("None,", ["None"]),
        (",None", ["None"]),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "csv, expected, env_var, config_attr",
        [
            *[
                (csv, exp, "RESTRICTED_TO_EMAIL_LIST_CSV", "RESTRICTED_TO_EMAIL_LIST")
                for csv, exp in [
                    ("recipient@example.com", ["recipient@example.com"]),
                    (
                        "r1@example.com,r2@example.com",
                        ["r1@example.com", "r2@example.com"],
                    ),
                    (
                        "r1@example.com, r2@example.com",
                        ["r1@example.com", "r2@example.com"],
                    ),
                    ("r1@example.com,", ["r1@example.com"]),
                    (",r1@example.com", ["r1@example.com"]),
                ]
                + COMMON_CSV_TEST_CASES
            ],
            *[
                (csv, exp, "ALLOWED_TOP_LEVEL_DOMAINS_CSV", "ALLOWED_TOP_LEVEL_DOMAINS")
                for csv, exp in [
                    (".gov", [".gov"]),
                    ("gov,mil", ["gov", "mil"]),
                    ("gov, mil", ["gov", "mil"]),
                    ("gov,", ["gov"]),
                    (",mil", ["mil"]),
                ]
                + COMMON_CSV_TEST_CASES
            ],
        ],
    )
    async def test_should_handle_parsing_csv_config(
        self,
        csv: str | None,
        expected: list[str],
        env_var: str,
        config_attr: str,
        mock_config_runtime_env_is_local: MagicMock,
    ) -> None:
        """Should parse CSV config correctly"""
        mock_config_runtime_env_is_local.return_value = True

        os.environ[env_var] = csv or ""

        config = Config()

        assert getattr(config, config_attr) == expected
