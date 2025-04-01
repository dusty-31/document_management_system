import pytest
from datetime import datetime

from models.document import Document
from services.external_integration import ExternalIntegration
from enums import DocumentTypeEnum


class TestExternalIntegration:
    @pytest.fixture
    def external_integration(self):
        return ExternalIntegration()

    def test_export_document(self, external_integration, document, user):
        """
        Test exporting document to external system.
        """
        result = external_integration.export_document(document, 'system1', user)

        assert result['success'] is True
        assert f'Document {document.title} successfully exported' in result['message']
        assert 'external_id' in result
        assert any(
            f"Document exported to system1 by {user.username}" in entry["entry_message"] for entry in document.history
        )

    def test_import_document(self, external_integration, user):
        """
        Test importing document from external system.
        """
        document = external_integration.import_document('crm', 'external_id_123', user)

        assert document is not None
        assert 'Imported from crm' in document.title
        assert 'external_id_123' in document.content
        assert document.author == user
        assert any(
            f"Document imported from crm by {user.username}" in entry["entry_message"] for entry in document.history
        )
