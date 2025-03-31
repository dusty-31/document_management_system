from enums import AccessLevelEnum
from .document import Document
from .user import User


class AccessControl:
    def __init__(self):
        self.document_access = {}  # {document.id: {user.id: access_level}}

    def grant_access(self, document: Document, user: User, level: AccessLevelEnum):
        """
        Grant access to a user for a specific document.
        """
        if document.id not in self.document_access:
            self.document_access[document.id] = {}

        self.document_access[document.id][user.id] = level
        user.documents.append(document)
        document.add_history_entry(f"Access granted to {user.username} with level {level.name}.")

    def revoke_access(self, document: Document, user: User):
        """
        Revoke access from a user for a specific document.
        """
        if document.id in self.document_access and user.id in self.document_access[document.id]:
            del self.document_access[document.id][user.id]
            user.documents.remove(document)
            document.add_history_entry(f"Access revoked from {user.username}.")
        else:
            raise ValueError(f"{user.username} does not have access to this document.")

    def check_access(self, document: Document, user: User, required_level: AccessLevelEnum) -> bool:
        """
        Check if a user has the required access level for a document.
        """
        if document.id in self.document_access and user.id in self.document_access[document.id]:
            user_level = self.document_access[document.id][user.id].value
            return user_level >= required_level.value
        return False
