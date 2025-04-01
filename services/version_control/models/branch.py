from typing import Optional


class Branch:
    """
    Represents a branch in the version control system.
    """

    def __init__(self, name: str, parent_branch_name: Optional[str] = None):
        self.name = name
        self.parent_branch_name = parent_branch_name
        self.versions = []  # list of versions in this branch
