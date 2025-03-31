from enum import Enum


class PositionEnum(Enum):
    """
    Enum representing different roles in a document management system.
    """
    ADMIN = "Admin"
    MANAGER = "Manager"
    HEAD = "Head of Department"
    EMPLOYEE = "Employee"
