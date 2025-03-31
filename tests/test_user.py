import pytest

from enums import AccessLevelEnum


class TestUser:
    @pytest.fixture
    def test_password(self):
        return "test_password_123"

    def test_user_creation(self, user, user_data):
        assert user.username == user_data["username"]
        assert user.password == user_data["password"]
        assert user.position == user_data["position"].value
        assert user.access_level == user_data["access_level"]
        assert isinstance(user.documents, list)
        assert len(user.documents) == 0
        assert user.id > 0

    def test_authenticate(self, user, user_data):
        assert user.authenticate(user_data["password"]) is True

    def test_authenticate_invalid(self, user, test_password):
        assert user.authenticate(test_password) is False

    def test_change_access_level(self, user):
        assert user.access_level == AccessLevelEnum.ADMIN

        new_access_level = AccessLevelEnum.READ_WRITE
        user.change_access_level(new_access_level)
        assert user.access_level == new_access_level
