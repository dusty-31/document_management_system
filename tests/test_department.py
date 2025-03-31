import pytest

from models.department import Department
from models.document import Document
from enums import DocumentTypeEnum


class TestDepartment:
    @pytest.fixture
    def second_user(self, user_data):
        from models.user import User

        return User(
            username=user_data["username"] + "_2",
            password=user_data["password"],
            position=user_data["position"],
            department=None,
            access_level=user_data["access_level"]
        )

    def test_create_object(self, user):
        department = Department(
            name="Test Department",
            head=user,
            members=[user]
        )
        assert department.name == "Test Department"
        assert department.head == user
        assert user in department.members
        assert len(department.members) == 2  # Head + 1 member

    def test_add_member(self, department, second_user):
        initial_members_count = len(department.members)
        department.add_member(user=second_user)

        assert second_user in department.members
        assert len(department.members) == initial_members_count + 1

    def test_remove_member(self, department, user, second_user):
        department.add_member(second_user)
        initial_members_count = len(department.members)
        department.remove_member(second_user)

        assert second_user not in department.members
        assert len(department.members) == initial_members_count - 1

    def test_remove_nonexistent_member(self, department, second_user):
        """
        Test removing a user who is not a member of the department.
        """
        with pytest.raises(ValueError) as error:
            department.remove_member(second_user)

        assert f"{second_user.username} is not a member of this department." in str(error.value)

    def test_get_all_members_documents(self, department, user):
        document = Document(
            title="Test Document",
            content="Test content",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT
        )
        user.documents.append(document)

        documents = department.get_all_members_documents()

        assert len(documents) == 1
        assert document in documents
        assert documents[0] == document
