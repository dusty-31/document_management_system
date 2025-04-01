import re
from typing import Set, List
from collections import Counter

from models.document import Document


class DocumentAnalytics:
    def __init__(self):
        self.document_keywords = {}  # {document_id: set(keywords)}
        self.keyword_index = {}  # {keyword: set(document_ids)}
        self.document_categories = {}  # {document_id: category}
        self.min_word_length = 3
        self.max_keywords = 10
        self.similarity_threshold = 0.8

        self.category_keywords = {
            'Financial': ['budget', 'finance', 'money', 'payment', 'expense', 'profit', 'cost'],
            'HR': ['staff', 'employee', 'personnel', 'worker', 'salary', 'vacation'],
            'Technical': ['system', 'program', 'equipment', 'server', 'technical', 'network'],
            'Legal': ['contract', 'agreement', 'law', 'legal', 'obligation', 'compliance'],
            'Marketing': ['advertising', 'marketing', 'sales', 'client', 'market', 'promotion']
        }

    def analyze_document(self, document: Document) -> Set[str]:
        """
        Analyzes the document to extract keywords and categorize it.
        """
        if not document or not document.content:
            return set()

        keywords = self._extract_keywords(document.content)
        self.document_keywords[document.id] = keywords

        for keyword in keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = set()
            self.keyword_index[keyword].add(document.id)

        category = self._categorize_document(keywords)
        self.document_categories[document.id] = category

        document.add_history_entry(f"Document analyzed and classified as '{category}'")

        return keywords

    def _extract_keywords(self, content: str) -> Set[str]:
        """
        Extracts keywords from the document content.
        """

        if not content:
            return set()

        words = re.sub(r'[^\w\s]', ' ', content.lower()).split()

        filtered_words = [word for word in words if len(word) >= self.min_word_length]
        word_freq = Counter(filtered_words)

        return set([word for word, _ in word_freq.most_common(self.max_keywords)])

    def _categorize_document(self, keywords: Set[str]) -> str:
        """
        Categorizes the document based on the extracted keywords.
        """

        category_scores = {category: 0 for category in self.category_keywords}

        for keyword in keywords:
            for category, category_words in self.category_keywords.items():
                for category_word in category_words:
                    if category_word in keyword:
                        category_scores[category] += 1

        max_score = 0
        best_category = "Not Categorized"

        for category, score in category_scores.items():
            if score > max_score:
                max_score = score
                best_category = category

        return best_category

    def find_duplicates(self, document: Document) -> List[int]:
        """
        Finds duplicate documents based on the analyzed keywords.
        """

        if document.id not in self.document_keywords:
            self.analyze_document(document)

        document_keywords = self.document_keywords[document.id]
        duplicates = []

        for doc_id, keywords in self.document_keywords.items():
            if doc_id != document.id:
                similarity = len(document_keywords.intersection(keywords)) / len(document_keywords.union(keywords))

                if similarity >= self.similarity_threshold:
                    duplicates.append(doc_id)

        return duplicates

    def find_related_documents(self, document: Document) -> List[int]:
        """
        Finds related documents based on the analyzed keywords.
        """
        if document.id not in self.document_keywords:
            self.analyze_document(document)

        document_keywords = self.document_keywords[document.id]
        related_documents = set()

        for keyword in document_keywords:
            if keyword in self.keyword_index:
                for doc_id in self.keyword_index[keyword]:
                    if doc_id != document.id:
                        related_documents.add(doc_id)

        return list(related_documents)
