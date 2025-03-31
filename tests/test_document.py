import pytest

from enums import DocumentTypeEnum, DocumentStatusEnum
from models.document import Document


class TestDocument:
    @pytest.fixture
    def document_payload(self, user):
        return {
            "title": "Test Document",
            "content": "This is a test document.",
            "author": user,
            "document_type": DocumentTypeEnum.CONTRACT,
        }

    def test_create_document(self, document_payload):
        document = Document(
            title=document_payload["title"],
            content=document_payload["content"],
            author=document_payload["author"],
            document_type=document_payload["document_type"]
        )

        assert document.title == document_payload["title"]
        assert document.content == document_payload["content"]
        assert document.author == document_payload["author"]
        assert document.document_type == document_payload["document_type"]
        assert document.status == DocumentStatusEnum.DRAFT
        assert isinstance(document.history, list)
        assert len(document.history) == 1
