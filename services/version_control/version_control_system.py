from datetime import datetime
from typing import Tuple, Optional, List, Dict

from models.document import Document
from models.user import User


class VersionControl:
    """
    Represents a version control system for documents.
    """

    def __init__(self):
        self.documents = {}  # example: {document_id: {branch_name: [versions]}}
        self.active_branches = {}  # example: {document_id: active_branch_name}
        self.locks = {}  # example: {document_id: user_id} - for document locking

    def initialize_version_control(self, document: Document) -> None:
        """
        Initializes version control for a new document.
        """
        if document.id not in self.documents:
            self.documents[document.id] = {
                "main": [
                    {
                        "version": 1,
                        "content": document.content,
                        "date": document.created_date,
                        "author": document.author
                    }
                ]
            }
            self.active_branches[document.id] = "main"
            document.add_history_entry("Version control system initialized")

    def create_branch(self, document: Document, branch_name: str, user: User) -> bool:
        """
        Creates a new branch from the current active branch.
        """

        if document.id not in self.documents:
            self.initialize_version_control(document)

        if branch_name in self.documents[document.id]:
            return False

        active_branch = self.active_branches[document.id]
        latest_version = self.documents[document.id][active_branch][-1]
        self.documents[document.id][branch_name] = [
            {
                "version": 1,
                "content": latest_version["content"],
                "date": datetime.now(),
                "author": user,
                "parent_branch": active_branch,
                "parent_version": len(self.documents[document.id][active_branch])
            }
        ]

        document.add_history_entry(f"Branch '{branch_name}' created by {user.username}")
        return True

    def switch_branch(self, document: Document, branch_name: str, user: User) -> bool:
        """
        Switches to a different branch for the document.
        """
        if document.id not in self.documents or branch_name not in self.documents[document.id]:
            return False

        self.active_branches[document.id] = branch_name
        latest_version = self.documents[document.id][branch_name][-1]
        document.content = latest_version["content"]
        document.version = len(self.documents[document.id][branch_name])
        document.add_history_entry(f"Switched to branch '{branch_name}' by {user.username}")
        return True

    def commit_changes(self, document: Document, user: User, description: str) -> bool:
        """
        Saves changes to the current active branch.
        """
        if document.id not in self.documents:
            self.initialize_version_control(document)

        active_branch = self.active_branches[document.id]

        latest_version = self.documents[document.id][active_branch][-1]
        if latest_version["content"] == document.content:
            return False

        next_version_number = len(self.documents[document.id][active_branch]) + 1
        self.documents[document.id][active_branch].append(
            {
                "version": next_version_number,
                "content": document.content,
                "date": datetime.now(),
                "author": user,
                "description": description
            }
        )
        document.version = next_version_number
        document.add_history_entry(
            f"Version {next_version_number} saved in branch '{active_branch}' by {user.username}: {description}")
        return True

    def merge_branches(
            self,
            document: Document,
            source_branch: str,
            target_branch: str,
            user: User
    ) -> Tuple[bool, str]:
        """
        Merges changes from one branch to another.
        """
        if document.id not in self.documents:
            return False, "Document not initialized for version control"

        if source_branch not in self.documents[document.id] or target_branch not in self.documents[document.id]:
            return False, "Specified branch does not exist"

        source_content = self.documents[document.id][source_branch][-1]["content"]
        target_content = self.documents[document.id][target_branch][-1]["content"]

        if source_content == target_content:
            return True, "Branches are identical, no merge needed"

        next_version_number = len(self.documents[document.id][target_branch]) + 1
        self.documents[document.id][target_branch].append(
            {
                "version": next_version_number,
                "content": source_content,
                "date": datetime.now(),
                "author": user,
                "description": f"Merged from branch '{source_branch}'",
                "merged_from": source_branch,
                "merged_version": len(self.documents[document.id][source_branch])
            }
        )

        document.add_history_entry(f"Merged branch '{source_branch}' into '{target_branch}' by {user.username}")
        return True, "Merge completed successfully"

    def resolve_conflict(self, document: Document, content: str, user: User, description: str) -> bool:
        """
        Resolves a merge conflict by creating a new version. Need user instance for conflict resolution.
        """
        if document.id not in self.documents:
            return False

        active_branch = self.active_branches[document.id]
        next_version_number = len(self.documents[document.id][active_branch]) + 1

        self.documents[document.id][active_branch].append(
            {
                "version": next_version_number,
                "content": content,
                "date": datetime.now(),
                "author": user,
                "description": f"Conflict resolution: {description}",
                "conflict_resolution": True
            }
        )

        document.content = content
        document.version = next_version_number
        document.add_history_entry(f"Conflict resolved by {user.username}: {description}")
        return True

    def get_version_history(self, document: Document, branch_name: Optional[str] = None) -> List[Dict]:
        """
        Gets the version history of the document for a specific branch.
        """
        if document.id not in self.documents:
            return []

        if branch_name is None:
            branch_name = self.active_branches[document.id]

        if branch_name not in self.documents[document.id]:
            return []

        return self.documents[document.id][branch_name]

    def checkout_version(self, document: Document, version_number: int, user: User) -> bool:
        """
        Returns the document to a specific version
        """
        if document.id not in self.documents:
            return False

        active_branch = self.active_branches[document.id]

        if version_number <= 0 or version_number > len(self.documents[document.id][active_branch]):
            return False

        target_version = self.documents[document.id][active_branch][version_number - 1]
        document.content = target_version["content"]

        document.add_history_entry(f"Reverted to version {version_number} by {user.username}")
        return True

    def lock_document(self, document: Document, user: User) -> bool:
        """
        Locks the document for editing
        """
        if document.id in self.locks:
            return False  # Document is already locked

        self.locks[document.id] = user.id
        document.add_history_entry(f"Document locked for editing by {user.username}")
        return True

    def unlock_document(self, document: Document, user: User) -> bool:
        """
        Unlocks the document for editing.
        """
        if document.id not in self.locks or self.locks[document.id] != user.id:
            return False

        del self.locks[document.id]
        document.add_history_entry(f"Document unlocked by {user.username}")
        return True

    def is_document_locked(self, document: Document) -> bool:
        """
        Checks if the document is locked for editing.
        """
        return document.id in self.locks

    def get_document_branches(self, document: Document) -> List[str]:
        """
        Returns a list of all branches for the specified document.
        """
        if document.id not in self.documents:
            return []

        return list(self.documents[document.id].keys())
