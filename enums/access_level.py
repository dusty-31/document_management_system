from enum import Enum


class AccessLevelEnum(Enum):
    """
    Enum representing different access levels in a document management system.
    """
    NO_ACCESS = 0
    READ_ONLY = 1
    READ_WRITE = 2
    OWNER = 3
    ADMIN = 4