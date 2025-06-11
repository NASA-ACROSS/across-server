from unittest.mock import MagicMock, patch

from across_server.auth.hashing import hash_secret_key


class TestHashing:
    def test_hash_secret_key_should_call_argon_password_hasher_hash(
        self,
    ) -> None:
        with patch(
            "across_server.auth.hashing.password_hasher"
        ) as mock_password_hasher:
            hash_secret_key("PASSWORD")
            mock_password_hasher.hash.assert_called_once()

    def test_hash_secret_key_should_call_argon_password_hasher_hash_with_peppered_arg(
        self, patch_config_secret: MagicMock
    ) -> None:
        # patch_config_secret fixes the pepper in hash_secret_key() to TEST_SECRET
        with patch(
            "across_server.auth.hashing.password_hasher"
        ) as mock_password_hasher:
            hash_secret_key("PASSWORD")

        assert mock_password_hasher.hash.call_args[0][0] == "PASSWORDTEST_SECRET"
