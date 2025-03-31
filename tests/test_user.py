import pytest

from enums import AccessLevelEnum
from models.user import User


class TestUser:
    @pytest.fixture
    def test_password(self):
        return "test_password_123"

    def test_create_object(self, user_data):
        user = User(
            username=user_data["username"],
            password=user_data["password"],
            position=user_data["position"],
            department=None,
            access_level=user_data["access_level"],
        )
        assert user.username == user_data["username"]
        assert user.password == user_data["password"]
        assert user.position == user_data["position"].value
        assert user.department is None
        assert user.access_level == user_data["access_level"]
        assert user.documents == []

    def test_authenticate(self, user, user_data):
        assert user.authenticate(user_data["password"]) is True

    def test_authenticate_invalid(self, user, test_password):
        assert user.authenticate(test_password) is False

    def test_change_access_level(self, user):
        assert user.access_level == AccessLevelEnum.ADMIN

        new_access_level = AccessLevelEnum.READ_WRITE
        user.change_access_level(new_access_level)
        assert user.access_level == new_access_level
