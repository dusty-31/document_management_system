import pytest
from datetime import datetime, timedelta

from enums import TaskStatusEnum, PositionEnum, AccessLevelEnum
from models.task import Task
from models.user import User


class TestTask:
    @pytest.fixture
    def task_deadline(self):
        return datetime.now() + timedelta(days=7)

    @pytest.fixture
    def task(self, document, user, task_deadline):
        return Task(document=document, deadline=task_deadline, assignee=user)

    def test_task_creation(self, task, document, user, task_deadline):
        task_instance = Task(
            document=document,
            deadline=task_deadline,
            assignee=user
        )
        assert task_instance.document == document
        assert task_instance.assignee == user
        assert task_instance.deadline == task_deadline
        assert task_instance.status == TaskStatusEnum.PENDING

    def test_create_task(self, document, user, task_deadline):
        task = Task.create_task(document=document, assignee=user, deadline=task_deadline)

        assert isinstance(task, Task)
        assert task.document == document
        assert task.assignee == user
        assert task.deadline == task_deadline
        assert task.status == TaskStatusEnum.PENDING

    def test_change_status(self, task):
        new_status = TaskStatusEnum.IN_PROGRESS
        task.change_status(new_status=new_status)

        assert task.status == new_status

    def test_change_status_invalid(self, task):
        with pytest.raises(ValueError) as error:
            task.change_status(new_status="Invalid Status")

        assert "Invalid status: 'Invalid Status'" in str(error.value)

    def test_assign_executor(self, task, user):
        new_assignee = User(
            username="new_assignee",
            password="password123",
            position=PositionEnum.MANAGER,
            department=None,
            access_level=AccessLevelEnum.READ_WRITE
        )

        initial_history_length = len(task.document.history)
        old_assignee = task.assignee

        task.assign_executor(new_assignee=new_assignee)

        assert task.assignee == new_assignee
        assert task.assignee != old_assignee

        assert len(task.document.history) == initial_history_length + 1
        assert "Task executor changed from" in task.document.history[-1]["entry_message"]
        assert old_assignee.username in task.document.history[-1]["entry_message"]
        assert new_assignee.username in task.document.history[-1]["entry_message"]
