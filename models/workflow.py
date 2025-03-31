from typing import List, Dict

from .document import Document
from enums import WorkflowStatusEnum, DocumentStatusEnum, DocumentTypeEnum, PositionEnum
from .user import User


class Workflow:
    global_workflow_id = 0
    ALLOWED_POSITIONS = [PositionEnum.MANAGER, PositionEnum.HEAD, PositionEnum.ADMIN]

    def __init__(self, document_type: DocumentTypeEnum, workflow_steps: List[Dict]) -> None:
        """
        Initialize the workflow for a specific document type.
        """
        self.id = self._get_workflow_id()
        self.document_type = document_type
        self.workflow_steps = workflow_steps
        self.current_step_index = 0
        self.status = WorkflowStatusEnum.IN_PROGRESS

    def _get_workflow_id(self) -> int:
        """
        Get a unique workflow ID from class variable.
        """

        self.global_workflow_id += 1
        return self.global_workflow_id

    def create_route(self, workflow_steps: List[Dict]) -> None:
        """
        Create a new workflow route.
        """

        self.workflow_steps = workflow_steps
        self.current_step_index = 0
        self.status = WorkflowStatusEnum.IN_PROGRESS

    def move_to_next_step(self, document: Document, user: User) -> bool:
        """
        Move the document to the next step in the workflow.
        """

        if self.status != WorkflowStatusEnum.IN_PROGRESS:
            raise ValueError("Workflow is not in progress.")

        if self.current_step_index >= len(self.workflow_steps):
            raise ValueError("No more steps in the workflow.")

        current_step = self.workflow_steps[self.current_step_index]

        if user.position not in self.ALLOWED_POSITIONS:
            raise PermissionError(f"{user.username} does not have permission to move to this step.")

        document.change_status(new_status=current_step["status"], editor=user)

        self.current_step_index += 1

        return True

    def complete_workflow(self, document: Document, user: User) -> None:
        """
        Complete the workflow for the document.
        """

        if self.status != WorkflowStatusEnum.IN_PROGRESS:
            raise ValueError("Workflow is not in progress.")

        if self.current_step_index < len(self.workflow_steps):
            raise ValueError("Workflow is not yet completed.")

        self.status = WorkflowStatusEnum.COMPLETED
        document.add_history_entry(entry_message=f"Workflow completed by {user.username}.")

        document.change_status(new_status=DocumentStatusEnum.APPROVED, editor=user)
        document.add_history_entry(entry_message=f"Document approved by {user.username}.")
