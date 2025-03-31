import pytest

from enums import AccessLevelEnum
from models.access_control import AccessControl
from models.user import User


class TestAccessControl:
    @pytest.fixture
    def access_control(self):
        return AccessControl()

    @pytest.fixture
    def second_user(self, user_data):
        return User(
            username=user_data["username"] + "_2",
            password=user_data["password"],
            position=user_data["position"],
            department=None,
            access_level=user_data["access_level"],
        )

    def test_access_control_creation(self, access_control):
        assert hasattr(access_control, 'document_access')
        assert isinstance(access_control.document_access, dict)
        assert len(access_control.document_access) == 0

    def test_grant_access(self, access_control, document, user):
        initial_history_length = len(document.history)

        access_control.grant_access(
            document=document,
            user=user,
            level=AccessLevelEnum.READ_ONLY,
        )

        assert document.id in access_control.document_access
        assert user.id in access_control.document_access[document.id]
        assert access_control.document_access[document.id][user.id] == AccessLevelEnum.READ_ONLY
        assert document in user.documents

        assert len(document.history) == initial_history_length + 1
        assert "Access granted to" in document.history[-1]["entry_message"]
        assert user.username in document.history[-1]["entry_message"]
        assert "READ" in document.history[-1]["entry_message"]

    def test_revoke_access(self, access_control, document, user):
        access_control.grant_access(
            document=document,
            user=user,
            level=AccessLevelEnum.READ_ONLY
        )
        initial_history_length = len(document.history)
        access_control.revoke_access(
            document=document,
            user=user
        )

        assert document.id in access_control.document_access
        assert user.id not in access_control.document_access[document.id]
        assert document not in user.documents

        assert len(document.history) == initial_history_length + 1
        assert "Access revoked from" in document.history[-1]["entry_message"]
        assert user.username in document.history[-1]["entry_message"]

    def test_revoke_nonexistent_access(self, access_control, document, user):
        with pytest.raises(ValueError) as error:
            access_control.revoke_access(
                document=document,
                user=user
            )

        assert f"{user.username} does not have access to this document." in str(error.value)

    def test_check_access_sufficient_level(self, access_control, document, user):
        access_control.grant_access(
            document=document,
            user=user,
            level=AccessLevelEnum.READ_WRITE
        )
        has_access = access_control.check_access(
            document=document,
            user=user,
            required_level=AccessLevelEnum.READ_ONLY
        )

        assert has_access is True

    def test_check_access_insufficient_level(self, access_control, document, user):
        access_control.grant_access(
            document=document,
            user=user,
            level=AccessLevelEnum.READ_ONLY
        )
        has_access = access_control.check_access(
            document=document,
            user=user,
            required_level=AccessLevelEnum.READ_WRITE
        )

        assert has_access is False

    def test_check_access_no_access(self, access_control, document, user):
        has_access = access_control.check_access(
            document=document,
            user=user,
            required_level=AccessLevelEnum.READ_ONLY
        )

        assert has_access is False
