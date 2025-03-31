import pytest

from enums import DocumentTypeEnum, DocumentStatusEnum
from models.search import Search
from models.document import Document


class TestSearch:
    @pytest.fixture
    def test_documents(self, user):
        doc1 = Document(
            title="Annual Report",
            content="Company activity report for 2023",
            author=user,
            document_type=DocumentTypeEnum.LETTER
        )
        doc1.status = DocumentStatusEnum.DRAFT

        doc2 = Document(
            title="Lease Agreement",
            content="Agreement for office space rental",
            author=user,
            document_type=DocumentTypeEnum.CONTRACT
        )
        doc2.status = DocumentStatusEnum.APPROVED

        doc3 = Document(
            title="Quarterly Report",
            content="Financial report for the first quarter",
            author=user,
            document_type=DocumentTypeEnum.LETTER
        )
        doc3.status = DocumentStatusEnum.REVIEW

        return [doc1, doc2, doc3]

    def test_search_creation(self):
        search = Search()
        assert search.criteria == {}
        criteria = {
            "title": "report",
            "status": "draft"
        }
        search_with_criteria = Search(criteria=criteria)
        assert search_with_criteria.criteria == criteria

    def test_execute_search_by_title(self, test_documents):
        criteria = {
            "title": "report"
        }
        search = Search(criteria=criteria)
        results = search.execute_search(documents=test_documents)

        assert len(results) == 2
        assert test_documents[0] in results  # Annual Report
        assert test_documents[2] in results  # Quarterly Report

    def test_execute_search_by_content(self, test_documents):
        criteria = {
            "content": "agreement"
        }
        search = Search(criteria=criteria)
        results = search.execute_search(documents=test_documents)

        assert len(results) == 1
        assert test_documents[1] in results  # Lease Agreement

    def test_execute_search_by_status(self, test_documents):
        criteria = {
            "status": "APPROVED"
        }
        search = Search(criteria=criteria)
        results = search.execute_search(documents=test_documents)

        assert len(results) == 1
        assert test_documents[1] in results  # Lease Agreement

        criteria = {
            "status": DocumentStatusEnum.DRAFT.value
        }
        search = Search(criteria=criteria)
        results = search.execute_search(documents=test_documents)

        assert len(results) == 1
        assert test_documents[0] in results  # Annual Report

    def test_execute_search_with_multiple_criteria(self, test_documents):
        criteria = {
            "title": "report",
            "status": "DRAFT"
        }
        search = Search(criteria=criteria)
        results = search.execute_search(documents=test_documents)

        assert len(results) == 1
        assert test_documents[0] in results  # Annual Report

    def test_set_criteria(self, test_documents):
        search = Search()
        criteria = {
            "title": "agreement"
        }
        search.set_criteria(criteria=criteria)

        results = search.execute_search(documents=test_documents)
        assert len(results) == 1
        assert test_documents[1] in results  # Lease Agreement

    def test_add_criteria(self, test_documents):
        criteria = {
            "title": "report"
        }
        search = Search(criteria=criteria)
        search.add_criteria(key="status", value="REVIEW")

        results = search.execute_search(documents=test_documents)
        assert len(results) == 1
        assert test_documents[2] in results  # Quarterly Report

    def test_clear_criteria(self, test_documents):
        criteria = {
            "title": "report"
        }
        search = Search(criteria=criteria)

        initial_results = search.execute_search(documents=test_documents)
        assert len(initial_results) == 2

        search.clear_criteria()
        assert search.criteria == {}

        all_results = search.execute_search(documents=test_documents)
        assert len(all_results) == len(test_documents)
