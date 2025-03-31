import pytest
from datetime import datetime, timedelta

from enums import AccessLevelEnum, ReportTypeEnum, DocumentTypeEnum, WorkflowStatusEnum, DocumentStatusEnum
from document_management_system import DocumentManagementSystem


class TestDocumentManagementSystem:
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
        dms.add_user(user)
        assert user in dms._users

    def test_add_duplicate_user(self, dms, user):
        dms.add_user(user)
        with pytest.raises(ValueError) as error:
            dms.add_user(user)
        assert "User already exists." in str(error.value)

    def test_remove_user(self, dms, user):
        dms.add_user(user)
        result = dms.remove_user(user.id)
        assert result is True
        assert user not in dms._users

    def test_remove_nonexistent_user(self, dms):
        result = dms.remove_user(999)
        assert result is False

    def test_create_document(self, dms, user):
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
