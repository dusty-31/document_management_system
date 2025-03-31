import pytest

from enums import WorkflowStatusEnum, DocumentStatusEnum, DocumentTypeEnum, PositionEnum
from models.workflow import Workflow
from models.document import Document


class TestWorkflow:
    @pytest.fixture
    def workflow_steps(self):
        return [
            {"step": "Review document content.", "status": DocumentStatusEnum.REVIEW},
            {"step": "Approve document.", "status": DocumentStatusEnum.APPROVAL},
            {"step": "Complete workflow.", "status": DocumentStatusEnum.ARCHIVED}
        ]

    @pytest.fixture
    def workflow(self, workflow_steps):
        return Workflow(document_type=DocumentTypeEnum.CONTRACT, workflow_steps=workflow_steps)

    @pytest.fixture
    def workflow_payload(self, workflow_steps):
        return {
            "document_type": "Contract",
            "workflow_steps": workflow_steps,
        }

    def test_workflow_creation(self, workflow, workflow_steps):
        workflow_instance = Workflow(
            document_type=DocumentTypeEnum.CONTRACT,
            workflow_steps=workflow_steps
        )

        assert workflow_instance.document_type == DocumentTypeEnum.CONTRACT
        assert workflow_instance.workflow_steps == workflow_steps
        assert workflow_instance.current_step_index == 0
        assert workflow_instance.status == WorkflowStatusEnum.IN_PROGRESS

    def test_create_route(self, workflow):
        new_workflow_steps = [
            {"step": "Draft", "status": DocumentStatusEnum.DRAFT},
            {"step": "Final", "status": DocumentStatusEnum.APPROVED}
        ]

        workflow.create_route(workflow_steps=new_workflow_steps)

        assert workflow.workflow_steps == new_workflow_steps
        assert workflow.current_step_index == 0
        assert workflow.status == WorkflowStatusEnum.IN_PROGRESS

    def test_move_to_next_step(self, workflow, user, document):
        user.position = PositionEnum.ADMIN
        initial_status = document.status

        result = workflow.move_to_next_step(document=document, user=user)

        assert result is True
        assert workflow.current_step_index == 1
        assert document.status != initial_status
        assert document.status == workflow.workflow_steps[0]["status"]
        assert len(document.history) > 1
        assert "Status changed from" in document.history[-1]["entry_message"]

    def test_move_to_next_step_permission_error(self, workflow, user, document):
        user.position = PositionEnum.EMPLOYEE

        with pytest.raises(PermissionError) as error:
            workflow.move_to_next_step(document=document, user=user)

        assert f"{user.username} does not have permission to move to this step." in str(error.value)
        assert workflow.current_step_index == 0

    def test_move_to_next_step_workflow_completed(self, workflow, user, document):
        workflow.status = WorkflowStatusEnum.COMPLETED

        with pytest.raises(ValueError) as error:
            workflow.move_to_next_step(document=document, user=user)

        assert "Workflow is not in progress." in str(error.value)

    def test_move_to_next_step_no_more_steps(self, workflow, user, document):
        workflow.current_step_index = len(workflow.workflow_steps)

        with pytest.raises(ValueError) as error:
            workflow.move_to_next_step(document=document, user=user)

        assert "No more steps in the workflow." in str(error.value)

    def test_complete_workflow(self, workflow, user, document):
        workflow.current_step_index = len(workflow.workflow_steps)
        workflow.complete_workflow(document=document, user=user)

        assert workflow.status == WorkflowStatusEnum.COMPLETED
        assert len(document.history) == 4

        assert "Workflow completed by" in document.history[-3]["entry_message"]
        assert "Status changed from" in document.history[-2]["entry_message"]
        assert "Document approved by" in document.history[-1]["entry_message"]

        assert document.status == DocumentStatusEnum.APPROVED

    def test_complete_workflow_not_in_progress(self, workflow, user, document):
        workflow.status = WorkflowStatusEnum.COMPLETED

        with pytest.raises(ValueError) as error:
            workflow.complete_workflow(document=document, user=user)

        assert "Workflow is not in progress." in str(error.value)

    def test_complete_workflow_not_completed(self, workflow, user, document):
        workflow.current_step_index = len(workflow.workflow_steps) - 1

        with pytest.raises(ValueError) as error:
            workflow.complete_workflow(document=document, user=user)

        assert "Workflow is not yet completed." in str(error.value)
