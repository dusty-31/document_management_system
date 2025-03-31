from datetime import datetime

from .document import Document
from .user import User
from enums import SignatureTypeEnum, DocumentStatusEnum


class ElectronicSignature:
    def __init__(self, user: User, date: datetime, signature_type: SignatureTypeEnum) -> None:
        self.user = user
        self.date = date
        self.signature_type = signature_type
        self.signature_data = None

    def sign_document(self, document: Document) -> bool:
        """
        Sign a document with the electronic signature.
        """
        if document.status != DocumentStatusEnum.APPROVAL:
            raise ValueError("Document must be in 'Approval' status to be signed.")

        self.signature_data = {
            "user": self.user.username,
            "date": self.date,
            "signature_type": self.signature_type.value,
        }
        document.add_history_entry(f"Document signed by {self.user.username} on {self.date}.")
        document.change_status(new_status=DocumentStatusEnum.APPROVED, editor=self.user)
        return True

    def verify_signature(self, document: Document) -> bool:
        """
        Verify the electronic signature on a document.
        """
        if not self.signature_data:
            raise ValueError("No signature data available to verify.")

        if document.status != DocumentStatusEnum.APPROVED:
            raise ValueError("Document must be in 'Approved' status to verify the signature.")

        return True
