from unittest.mock import MagicMock

from across_server.auth.hashing import hash_secret_key


class TestHashing:
    def test_hash_secret_key_should_generate_the_same_hash_deterministically(
        self, patch_config_secret: MagicMock
    ) -> None:
        # patch_config_secret fixes the pepper in hash_secret_key() to TEST_SECRET
        hashed_secret = hash_secret_key("PASSWORD", "SALT")
        assert (
            hashed_secret
            == "ad47942fc24671df80afc83b459ae79e26f097e9b4b1c7374f9b63dc6b590f57205cb69d4309a250ceeca9e0f4c5b1a74a40dcabf8163af34c2ccc13d7de9e09"
        )
