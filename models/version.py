from datetime import datetime

from .user import User


class Version:
    def __init__(self, version_number: str, author: User, description: str) -> None:
        self.version_number = version_number
        self.author = author
        self.description = description
        self.date_of_change = datetime.now()

    @classmethod
    def create_version(cls, version_number: str, author: User, description: str) -> "Version":
        """
        Create a new version of the document.
        """
        return cls(version_number=version_number, author=author, description=description)

    def compare_versions(self, other_version: "Version") -> bool:
        """
        Compare two versions of the document.
        """
        return self.version_number == other_version.version_number
