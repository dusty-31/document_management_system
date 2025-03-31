from enum import Enum


class TaskStatusEnum(Enum):
    """
    Enum representing different statuses of a task in the system.
    """
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
