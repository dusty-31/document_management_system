from enum import Enum


class ReportTypeEnum(Enum):
    """
    Enum representing different types of reports that can be generated.
    """
    SUMMARY = "Summary"
    DOCUMENT_STATUS = "Document Status"
    DETAILED = "Detailed"
    STATISTICAL = "Statistical"
    CUSTOM = "Custom"