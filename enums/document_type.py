from enum import Enum


class DocumentTypeEnum(Enum):
    """
    Enum representing different types of documents in the system.
    """
    CONTRACT = "Contract"
    LETTER = "Letter"
    POLICY = "Policy"
