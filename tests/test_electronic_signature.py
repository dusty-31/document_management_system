import pytest
from datetime import datetime

from enums import SignatureTypeEnum, DocumentStatusEnum
from models.electronic_signature import ElectronicSignature


class TestElectronicSignature:
    @pytest.fixture
    def signature_data(self):
        return {
            "date": datetime.now(),
            "signature_type": SignatureTypeEnum.DIGITAL
        }

    @pytest.fixture
    def electronic_signature(self, user, signature_data):
        return ElectronicSignature(
            user=user,
            date=signature_data["date"],
            signature_type=signature_data["signature_type"]
        )

    def test_electronic_signature_creation(self, electronic_signature, user, signature_data):
        assert electronic_signature.user == user
        assert electronic_signature.date == signature_data["date"]
        assert electronic_signature.signature_type == signature_data["signature_type"]
        assert electronic_signature.signature_data is None

    def test_sign_document(self, electronic_signature, document, user):
        document.status = DocumentStatusEnum.APPROVAL
        initial_history_length = len(document.history)
        result = electronic_signature.sign_document(document=document)

        assert result is True

        assert len(document.history) > initial_history_length
        assert "Document signed by" in document.history[-2]["entry_message"]
        assert user.username in document.history[-2]["entry_message"]

        assert document.status == DocumentStatusEnum.APPROVED

    def test_sign_document_wrong_status(self, electronic_signature, document):
        document.status = DocumentStatusEnum.DRAFT

        with pytest.raises(ValueError) as error:
            electronic_signature.sign_document(document=document)

        assert "Document must be in 'Approval' status to be signed." in str(error.value)

    def test_verify_signature(self, electronic_signature, document, user):
        document.status = DocumentStatusEnum.APPROVAL
        electronic_signature.sign_document(document=document)
        result = electronic_signature.verify_signature(document=document)

        assert result is True

    def test_verify_signature_wrong_status(self, electronic_signature, document, user):
        document.status = DocumentStatusEnum.APPROVAL
        electronic_signature.sign_document(document=document)
        document.status = DocumentStatusEnum.DRAFT

        with pytest.raises(ValueError) as error:
            electronic_signature.verify_signature(document=document)

        assert "Document must be in 'Approved' status to verify the signature." in str(error.value)
