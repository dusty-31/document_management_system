from datetime import datetime

from .document import Document
from enums import TaskStatusEnum
from .user import User


class Task:
    global_task_id = 0

    def __init__(self, document: Document, deadline: datetime, assignee: User = None) -> None:
        self.id = self._get_task_id()
        self.document = document
        self.assignee = assignee
        self.deadline = deadline
        self.status = TaskStatusEnum.PENDING

    def _get_task_id(self) -> int:
        """
        Get a unique task ID from class variable.
        """

        self.global_task_id += 1
        return self.global_task_id

    @classmethod
    def create_task(cls, document: Document, assignee: User, deadline: datetime) -> "Task":
        """
        Create a new task for a document.
        """

        return cls(document=document, assignee=assignee, deadline=deadline)

    def change_status(self, new_status: TaskStatusEnum) -> None:
        """
        Change the status of the task.
        """
        if new_status not in TaskStatusEnum:
            raise ValueError(f"Invalid status: '{new_status}'")

        self.status = new_status

    def assign_executor(self, new_assignee: User) -> None:
        """
        Assign a new executor to the task.
        """
        old_assignee = self.assignee
        self.assignee = new_assignee
        self.document.add_history_entry(
            f"Task executor changed from {old_assignee.username} to {new_assignee.username}."
        )
