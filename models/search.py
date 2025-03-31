from typing import Dict, List

from .document import Document
from enums import DocumentStatusEnum


class Search:
    def __init__(self, criteria: Dict[str, str] = None) -> None:
        self.criteria = criteria or {}

    def execute_search(self, documents: List[Document]) -> List[Document]:
        results = documents

        if 'title' in self.criteria:
            title_query = self.criteria['title'].lower()
            results = [doc for doc in results if title_query in doc.title.lower()]

        if 'author' in self.criteria:
            author_name = self.criteria['author'].lower()
            results = [doc for doc in results if
                       hasattr(doc.author, 'username') and author_name in doc.author.username.lower()]

        if 'content' in self.criteria:
            content_query = self.criteria['content'].lower()
            results = [doc for doc in results if content_query in doc.content.lower()]

        if 'status' in self.criteria:
            status = self.criteria['status']
            if isinstance(status, str):
                status = DocumentStatusEnum[status.upper()]
            results = [doc for doc in results if doc.status == status]

        return results

    def set_criteria(self, criteria: Dict[str, str]) -> None:
        """
        Set search criteria.
        """
        self.criteria = criteria

    def add_criteria(self, key: str, value: str) -> None:
        """
        Add a single search criterion.
        """
        self.criteria[key] = value

    def clear_criteria(self) -> None:
        """
        Clear all search criteria.
        """
        self.criteria = {}
