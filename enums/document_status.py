from enum import Enum


class DocumentStatusEnum(Enum):
    """
    Enum representing different statuses of a document in the system.
    """
    DRAFT = "Draft"
    REVIEW = "Review"
    APPROVAL = "Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"
