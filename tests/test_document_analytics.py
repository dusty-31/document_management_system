import pytest
from models.document import Document
from models.user import User
from enums import DocumentTypeEnum, PositionEnum, AccessLevelEnum
from services.document_analytics import DocumentAnalytics


class TestDocumentAnalytics:
    @pytest.fixture
    def user(self):
        return User(
            username="test_user",
            password="password123",
            position=PositionEnum.MANAGER,
            department=None,
            access_level=AccessLevelEnum.ADMIN,
        )

    @pytest.fixture
    def document(self, user):
        return Document(
            title="Financial Report",
            content="This is a financial report with budget planning and expense analysis.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT
        )

    @pytest.fixture
    def document_analytics(self):
        return DocumentAnalytics()

    def test_create_object(self):
        analytics = DocumentAnalytics()

        assert analytics is not None
        assert isinstance(analytics, DocumentAnalytics)
        assert isinstance(analytics.document_keywords, dict)
        assert isinstance(analytics.keyword_index, dict)
        assert isinstance(analytics.document_categories, dict)

    def test_analyze_document(self, document_analytics, document):
        keywords = document_analytics.analyze_document(document)

        assert keywords is not None
        assert isinstance(keywords, set)
        assert len(keywords) > 0
        assert document.id in document_analytics.document_keywords
        assert any("analyzed and classified" in entry["entry_message"] for entry in document.history)

    def test_extract_keywords(self, document_analytics, document):
        keywords = document_analytics._extract_keywords(document.content)

        assert isinstance(keywords, set)
        assert len(keywords) > 0
        assert any(keyword in keywords for keyword in ["financial", "report", "budget", "expense"])

    def test_categorize_document(self, document_analytics, document):
        keywords = document_analytics._extract_keywords(document.content)
        category = document_analytics._categorize_document(keywords)

        assert category is not None
        assert isinstance(category, str)
        assert category == "Financial"

    def test_find_duplicates(self, document_analytics, document, user):
        similar_doc = Document(
            title="Similar Financial Report",
            content="This is a financial report with budget planning and expense analysis.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT
        )

        document_analytics.analyze_document(document)
        document_analytics.analyze_document(similar_doc)
        duplicates = document_analytics.find_duplicates(document)

        assert isinstance(duplicates, list)
        assert similar_doc.id in duplicates

    def test_find_related_documents(self, document_analytics, document, user):
        related_doc = Document(
            title="Budget Planning",
            content="This document covers budget planning for the financial year.",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT
        )
        unrelated_doc = Document(
            title="HR Policy",
            content="This HR policy document describes employee benefits and vacation policies.",
            author=user,
            document_type=DocumentTypeEnum.POLICY
        )
        document_analytics.analyze_document(document)
        document_analytics.analyze_document(related_doc)
        document_analytics.analyze_document(unrelated_doc)
        related = document_analytics.find_related_documents(document)

        assert isinstance(related, list)
        assert related_doc.id in related
