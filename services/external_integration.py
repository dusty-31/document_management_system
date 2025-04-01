from typing import Dict, Any, Optional

from models.document import Document
from models.user import User
from enums import DocumentTypeEnum


class ExternalIntegration:
    """
    Represents the external integration system for document management.
    """

    def __init__(self):
        self.external_systems = {
            'system1': {
                'name': 'Some System',
                'api_endpoint': 'https://system1-example.com',
                'enabled': True
            },
            'system2': {
                'name': 'Some System2',
                'api_endpoint': 'https://system2-example.com',
                'enabled': False
            },
            'e_signature': {
                'name': 'E-Signature System',
                'api_endpoint': 'https://e-signature-example.com',
                'enabled': True
            }
        }

    def export_document(self, document: Document, system_type: str, user: User) -> Dict[str, Any]:
        """
        Exports a document to an external system
        """
        if system_type not in self.external_systems:
            return {
                'success': False,
                'error': f'Unknown system type: {system_type}'
            }

        if not self.external_systems[system_type]['enabled']:
            return {
                'success': False,
                'error': f'System {system_type} is disabled'
            }

        document.add_history_entry(f"Document exported to {system_type} by {user.username}")

        return {
            'success': True,
            'message': f'Document {document.title} successfully exported to {system_type}',
            'external_id': f'ext_{system_type}_{document.id}'
        }

    def import_document(self, system_type: str, external_id: str, user: User) -> Optional[Document]:
        """
        Imports a document from an external system
        """
        if system_type not in self.external_systems:
            return None

        if not self.external_systems[system_type]['enabled']:
            return None

        document = Document(
            title=f'Imported from {system_type} - {external_id}',
            content=f'This document was imported from {system_type} with ID {external_id}',
            author=user,
            document_type=DocumentTypeEnum.CONTRACT
        )

        document.add_history_entry(f"Document imported from {system_type} by {user.username}")

        return document
