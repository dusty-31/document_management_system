import pytest
from datetime import datetime, timedelta

from enums import AccessLevelEnum, ReportTypeEnum, DocumentTypeEnum, WorkflowStatusEnum, DocumentStatusEnum
from document_management_system import DocumentManagementSystem


class TestDocumentManagementSystem:
    """
    Test suite for the Document Management System (DMS) class.
    """

    @pytest.fixture
    def dms(self):
        # Reset singleton instance for each test
        if DocumentManagementSystem in DocumentManagementSystem._instances:
            del DocumentManagementSystem._instances[DocumentManagementSystem]
        return DocumentManagementSystem()

    def test_singleton_pattern(self, dms):
        dms2 = DocumentManagementSystem()
        assert dms is dms2

    def test_add_user(self, dms, user):
        """
        Test adding a user to the main system.
        """

        dms.add_user(user)
        assert user in dms._users

    def test_add_duplicate_user(self, dms, user):
        """
        Test adding a duplicate user to the main system.
        """

        dms.add_user(user)
        with pytest.raises(ValueError) as error:
            dms.add_user(user)
        assert "User already exists." in str(error.value)

    def test_remove_user(self, dms, user):
        """
        Test removing a user from the main system.
        """

        dms.add_user(user)
        result = dms.remove_user(user.id)
        assert result is True
        assert user not in dms._users

    def test_remove_nonexistent_user(self, dms):
        """
        Test removing a user that does not exist in the system.
        """

        result = dms.remove_user(999)
        assert result is False

    def test_create_document(self, dms, user):
        """
        Test creating a document in the main system.
        """

        dms.add_user(user)
        document = dms.create_document(
            title="Test Document",
            content="This is a test document.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT,
        )

        assert document in dms._documents
        assert document.title == "Test Document"
        assert document.content == "This is a test document."
        assert document.author == user

    def test_assign_task(self, dms, user, document):
        """
        Test assigning a task to a user for a specific document.
        """

        dms.add_user(user)
        deadline = datetime.now() + timedelta(days=7)

        task = dms.assign_task(
            document=document,
            assignee=user,
            deadline=deadline
        )

        assert task in dms._tasks
        assert task.document == document
        assert task.assignee == user
        assert task.deadline == deadline

    def test_generate_report(self, dms, document, user):
        """
        Test generating a report for a specific document.
        """

        dms.add_user(user)
        dms._documents.append(document)

        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        report = dms.generate_report(
            report_type=ReportTypeEnum.DOCUMENT_STATUS,
            start_date=start_date,
            end_date=end_date
        )

        assert report is not None
        assert report.report_type == ReportTypeEnum.DOCUMENT_STATUS
        assert report.period == (start_date, end_date)

    def test_create_workflow(self, dms):
        """
        Test creating a workflow for a specific document type.
        """

        workflow_steps = [
            {"step": "Review", "status": DocumentStatusEnum.REVIEW},
            {"step": "Approve", "status": DocumentStatusEnum.APPROVAL},
            {"step": "Publish", "status": DocumentStatusEnum.APPROVED}
        ]

        workflow = dms.create_workflow(
            document_type=DocumentTypeEnum.CONTRACT,
            workflow_steps=workflow_steps
        )

        assert workflow in dms._workflows
        assert workflow.document_type == DocumentTypeEnum.CONTRACT
        assert workflow.workflow_steps == workflow_steps
        assert workflow.current_step_index == 0
        assert workflow.status == WorkflowStatusEnum.IN_PROGRESS

    def test_assign_workflow_to_document(self, dms, document, user):
        """
        Test assigning a workflow to a specific document.
        """

        dms.add_user(user)
        dms._documents.append(document)

        dms._access_control.grant_access(document, user, AccessLevelEnum.READ_WRITE)

        workflow_steps = [
            {"step": "Review", "status": DocumentStatusEnum.REVIEW},
            {"step": "Approve", "status": DocumentStatusEnum.APPROVAL}
        ]
        workflow = dms.create_workflow(DocumentTypeEnum.CONTRACT, workflow_steps)

        initial_history_length = len(document.history)

        result = dms.assign_workflow_to_document(document, workflow, user)

        assert result is True
        assert len(document.history) > initial_history_length
        assert "Workflow assigned by" in document.history[-1]["entry_message"]
        assert user.username in document.history[-1]["entry_message"]

    def test_get_workflows_by_document_type(self, dms):
        """
        Test retrieving workflows by document type.
        """

        contract_workflow1 = dms.create_workflow(
            DocumentTypeEnum.CONTRACT,
            [{"step": "Review", "status": DocumentStatusEnum.REVIEW}]
        )
        contract_workflow2 = dms.create_workflow(
            DocumentTypeEnum.CONTRACT,
            [{"step": "Publish", "status": DocumentStatusEnum.APPROVED}]
        )
        report_workflow = dms.create_workflow(
            DocumentTypeEnum.LETTER,
            [{"step": "Review", "status": DocumentStatusEnum.APPROVAL}]
        )

        contract_workflows = dms.get_workflows_by_document_type(DocumentTypeEnum.CONTRACT)

        assert len(contract_workflows) == 2
        assert contract_workflow1 in contract_workflows
        assert contract_workflow2 in contract_workflows
        assert report_workflow not in contract_workflows

        report_workflows = dms.get_workflows_by_document_type(DocumentTypeEnum.LETTER)

        assert len(report_workflows) == 1
        assert report_workflow in report_workflows

    def test_create_document_with_version_control(self, dms, user):
        """
        Test creating a document with version control enabled.
        """

        dms.add_user(user)
        document = dms.create_document(
            title="Version Control Test",
            content="This is a test document for version control.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT,
        )

        assert document.id in dms._version_control.documents
        assert "main" in dms._version_control.documents[document.id]
        assert len(dms._version_control.documents[document.id]["main"]) == 1
        assert dms._version_control.documents[document.id]["main"][0]["content"] == document.content
        assert any("Version control system initialized" in entry["entry_message"] for entry in document.history)

    def test_create_branch(self, dms, user):
        """
        Test creating a branch from the main document version.
        """

        dms.add_user(user)
        document = dms.create_document(
            title="Branch Test",
            content="This is a test document for branch creation.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT,
        )

        result = dms.create_branch(document, "feature", user)

        assert result is True
        assert "feature" in dms._version_control.documents[document.id]
        assert len(dms._version_control.documents[document.id]["feature"]) == 1
        assert dms._version_control.documents[document.id]["feature"][0]["content"] == document.content
        assert any("Branch 'feature' created by" in entry["entry_message"] for entry in document.history)

    def test_commit_changes(self, dms, user):
        """
        Test committing changes to the main document version.
        """

        dms.add_user(user)
        document = dms.create_document(
            title="Commit Test",
            content="This is the initial content.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT,
        )

        document.content = "This is the updated content."
        result = dms.commit_changes(document, user, "Update content")

        assert result is True
        assert len(dms._version_control.documents[document.id]["main"]) == 2
        assert dms._version_control.documents[document.id]["main"][1]["content"] == "This is the updated content."
        assert dms._version_control.documents[document.id]["main"][1]["description"] == "Update content"
        assert any("Version 2 saved in branch 'main'" in entry["entry_message"] for entry in document.history)

    def test_merge_branches(self, dms, user):
        """
        Test merging changes from one branch into another.
        """

        dms.add_user(user)
        document = dms.create_document(
            title="Merge Test",
            content="This is the initial content.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT,
        )

        dms.create_branch(document, "feature", user)
        dms._version_control.switch_branch(document, "feature", user)
        document.content = "This is content on the feature branch."
        dms.commit_changes(document, user, "Update content on feature branch")
        dms._version_control.switch_branch(document, "main", user)
        result, message = dms.merge_branches(document, "feature", "main", user)

        assert result is True
        assert "successfully" in message
        assert len(dms._version_control.documents[document.id]["main"]) == 2
        assert dms._version_control.documents[document.id]["main"][1][
                   "content"] == "This is content on the feature branch."

        assert any("Merged branch 'feature' into 'main'" in entry["entry_message"] for entry in document.history)

    def test_get_document_history(self, dms, user):
        """
        Test retrieving the version history of a document.
        """

        dms.add_user(user)
        document = dms.create_document(
            title="History Test",
            content="This is the initial content.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT,
        )

        document.content = "First update."
        dms.commit_changes(document, user, "First change")

        document.content = "Second update."
        dms.commit_changes(document, user, "Second change")

        history = dms.get_document_version_history(document)

        assert len(history) == 3
        assert history[0]["version"] == 1
        assert history[0]["content"] == "This is the initial content."
        assert history[1]["version"] == 2
        assert history[1]["content"] == "First update."
        assert history[1]["description"] == "First change"
        assert history[2]["version"] == 3
        assert history[2]["content"] == "Second update."
        assert history[2]["description"] == "Second change"

    def test_export_document_to_external_system(self, dms, document, user):
        """
        Test exporting a document to an external system.
        """

        dms.add_user(user)
        dms._documents.append(document)
        result = dms.export_document_to_external_system(document, 'system1', user)

        assert result['success'] is True
        assert f'Document {document.title} successfully exported' in result['message']
        assert any(
            f"Document exported to system1 by {user.username}" in entry["entry_message"] for entry in document.history
        )

    def test_import_document_from_external_system(self, dms, user, document):
        """
        Test importing a document from an external system.
        """

        dms.add_user(user)

        initial_document_count = len(dms._documents)
        document = dms.import_document_from_external_system('system1', 'external_id_123', user)

        assert document is not None
        assert len(dms._documents) == initial_document_count + 1
        assert document in dms._documents
        assert 'Imported from system1' in document.title
        assert any(f"Document imported from system1 by {user.username}" in entry["entry_message"]
                   for entry in document.history)

        assert dms._access_control.check_access(document, user, AccessLevelEnum.OWNER)

        if hasattr(dms, '_version_control'):
            assert document.id in dms._version_control.documents
