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

    def test_create_object(self, document_payload):
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

    def test_update_content(self, document_payload, user):
        document = Document(
            title=document_payload["title"],
            content=document_payload["content"],
            author=document_payload["author"],
            document_type=document_payload["document_type"]
        )
        new_content = "This is the updated content."
        document.update_content(new_content=new_content, editor=user)

        assert document.content == new_content
        assert document.version == 2
        assert len(document.history) == 2
        assert "Content updated by" in document.history[-1]["entry_message"]

    def test_document_status_change(self, document_payload, user):
        document = Document(
            title=document_payload["title"],
            content=document_payload["content"],
            author=document_payload["author"],
            document_type=document_payload["document_type"]
        )
        new_status = DocumentStatusEnum.REVIEW
        document.change_status(new_status=new_status, editor=user)

        assert document.status == new_status
        assert len(document.history) == 2
        assert "Status changed from" in document.history[-1]["entry_message"]

    def test_add_history_entry(self, document_payload):
        document = Document(
            title=document_payload["title"],
            content=document_payload["content"],
            author=document_payload["author"],
            document_type=document_payload["document_type"]
        )
        entry_message = "Test history entry."
        document.add_history_entry(entry_message=entry_message)

        assert len(document.history) == 2
        assert document.history[-1]["entry_message"] == entry_message
