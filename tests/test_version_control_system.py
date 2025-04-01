import pytest

from models.document import Document
from models.user import User
from services.version_control.version_control_system import VersionControl
from enums import DocumentTypeEnum, PositionEnum, AccessLevelEnum


class TestVersionControl:
    @pytest.fixture
    def user(self):
        return User(
            username="test_user",
            password="password123",
            position=PositionEnum.MANAGER,
            department=None,
            access_level=AccessLevelEnum.ADMIN,
        )

    @pytest.fixture
    def second_user(self):
        return User(
            username="second_user",
            password="password456",
            position=PositionEnum.EMPLOYEE,
            department=None,
            access_level=AccessLevelEnum.READ_WRITE,
        )

    @pytest.fixture
    def document(self, user):
        return Document(
            title="Test Document",
            content="This is the initial content.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT
        )

    @pytest.fixture
    def version_control(self):
        return VersionControl()

    def test_create_version_control(self):
        """
        Test creating a VersionControl object.
        """
        version_control = VersionControl()

        assert version_control is not None
        assert isinstance(version_control, VersionControl)
        assert isinstance(version_control.documents, dict)
        assert isinstance(version_control.active_branches, dict)
        assert isinstance(version_control.locks, dict)

    def test_initialize_version_control(self, version_control, document):
        """
        Test initializing version control for a document.
        """
        version_control.initialize_version_control(document)

        assert document.id in version_control.documents
        assert "main" in version_control.documents[document.id]
        assert len(version_control.documents[document.id]["main"]) == 1
        assert version_control.documents[document.id]["main"][0]["content"] == document.content
        assert document.id in version_control.active_branches
        assert version_control.active_branches[document.id] == "main"
        assert any("Version control system initialized" in entry["entry_message"] for entry in document.history)

    def test_create_branch(self, version_control, document, user):
        """
        Test creating a new branch for a document.
        """
        version_control.initialize_version_control(document)
        result = version_control.create_branch(document, "feature", user)

        assert result is True
        assert "feature" in version_control.documents[document.id]
        assert len(version_control.documents[document.id]["feature"]) == 1
        assert version_control.documents[document.id]["feature"][0]["content"] == document.content
        assert any("Branch 'feature' created by" in entry["entry_message"] for entry in document.history)

    def test_switch_branch(self, version_control, document, user):
        """
        Test switching to another branch.
        """
        version_control.initialize_version_control(document)
        version_control.create_branch(document, "feature", user)

        # Modify document content and commit to feature branch
        document.content = "This is content on the feature branch."
        version_control.switch_branch(document, "feature", user)
        version_control.commit_changes(document, user, "Update content on feature branch")

        # Switch back to main branch
        result = version_control.switch_branch(document, "main", user)

        assert result is True
        assert version_control.active_branches[document.id] == "main"
        assert document.content == "This is the initial content."
        assert any("Switched to branch 'main' by" in entry["entry_message"] for entry in document.history)

    def test_commit_changes(self, version_control, document, user):
        """
        Test committing changes to a document.
        """
        version_control.initialize_version_control(document)

        document.content = "This is the updated content."
        result = version_control.commit_changes(document, user, "Update content")

        assert result is True
        assert len(version_control.documents[document.id]["main"]) == 2
        assert version_control.documents[document.id]["main"][1]["content"] == "This is the updated content."
        assert version_control.documents[document.id]["main"][1]["description"] == "Update content"
        assert document.version == 2
        assert any("Version 2 saved in branch 'main' by" in entry["entry_message"] for entry in document.history)

    def test_merge_branches(self, version_control, document, user):
        """
        Test merging branches.
        """
        version_control.initialize_version_control(document)
        version_control.create_branch(document, "feature", user)
        version_control.switch_branch(document, "feature", user)
        document.content = "This is content on the feature branch."
        version_control.commit_changes(document, user, "Update content on feature branch")
        version_control.switch_branch(document, "main", user)
        result, message = version_control.merge_branches(document, "feature", "main", user)

        assert result is True
        assert "Merge completed successfully" in message
        assert len(version_control.documents[document.id]["main"]) == 2
        assert version_control.documents[document.id]["main"][1]["content"] == "This is content on the feature branch."
        assert "Merged from branch 'feature'" in version_control.documents[document.id]["main"][1]["description"]
        assert any("Merged branch 'feature' into 'main' by" in entry["entry_message"] for entry in document.history)

    def test_get_version_history(self, version_control, document, user):
        """
        Test getting version history of a document.
        """
        version_control.initialize_version_control(document)

        document.content = "This is the first update."
        version_control.commit_changes(document, user, "First update")

        document.content = "This is the second update."
        version_control.commit_changes(document, user, "Second update")
        history = version_control.get_version_history(document)

        assert len(history) == 3
        assert history[0]["version"] == 1
        assert history[0]["content"] == "This is the initial content."
        assert history[1]["version"] == 2
        assert history[1]["content"] == "This is the first update."
        assert history[2]["version"] == 3
        assert history[2]["content"] == "This is the second update."
