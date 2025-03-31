from enum import Enum


class WorkflowStatusEnum(Enum):
    """
    Enum representing different statuses of a workflow in the system.
    """
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"