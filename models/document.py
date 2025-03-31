from datetime import datetime
from typing import List, Dict, Union

from enums import DocumentStatusEnum, DocumentTypeEnum
from .user import User


class Document:
    global_document_id = 0

    BLOCKED_UPDATE_STATUSES = [DocumentStatusEnum.APPROVED, DocumentStatusEnum.REJECTED, DocumentStatusEnum.ARCHIVED]

    def __init__(self, title: str, content: str, author: User, document_type: DocumentTypeEnum) -> None:
        self.id = self._get_document_id()
        self.title = title
        self.content = content
        self.author = author
        self.created_date = datetime.now()
        self.last_modified_date = datetime.now()
        self.status = DocumentStatusEnum.DRAFT
        self.document_type = document_type
        self.version = 1
        self.history = []

        self.add_history_entry(entry_message="Document created.")

    @classmethod
    def _get_document_id(cls) -> int:
        """
        Get a unique document ID from class variable.
        """

        cls.global_document_id += 1
        return cls.global_document_id

    def add_history_entry(self, entry_message: str) -> None:
        """
        Adds an entry to the document's history.
        """

        self.history.append({
            "entry_message": entry_message,
            "timestamp": datetime.now(),
        })

    def update_content(self, new_content: str, editor: User) -> None:
        """
        Update the content of the document.
        """

        if self.status in self.BLOCKED_UPDATE_STATUSES:
            raise ValueError(f"Cannot edit an {self.status.value} document.")

        self.content = new_content
        self.last_modified_date = datetime.now()
        self.version += 1
        self.add_history_entry(entry_message=f"Content updated by {editor}.")

    def change_status(self, new_status: DocumentStatusEnum, editor: User) -> None:
        """
        Change the status of the document.
        """

        if self.status in self.BLOCKED_UPDATE_STATUSES:
            raise ValueError(f"Cannot change status of an {self.status.value} document.")

        old_status: DocumentStatusEnum = self.status
        self.status = new_status
        self.last_modified_date = datetime.now()
        self.add_history_entry(
            entry_message=f"Status changed from \'{old_status.value}\' to \'{new_status.value}\' by {editor.username}.",
        )

    def get_history(self) -> List[Dict[str, Union[str, datetime]]]:
        """
        Get the history of the document.
        """

        return self.history
