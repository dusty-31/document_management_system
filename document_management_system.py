from datetime import datetime
from typing import List, Set, Tuple, Dict

from models.access_control import AccessControl
from models.document import Document
from enums import AccessLevelEnum, ReportTypeEnum, DocumentTypeEnum
from models.report import Report
from models.search import Search
from models.task import Task
from models.user import User
from models.workflow import Workflow
from services.document_analytics import DocumentAnalytics
from services.version_control.version_control_system import VersionControl


class SingletonMeta(type):
    """
    Singleton metaclass to ensure only one instance of the class exists.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DocumentManagementSystem(metaclass=SingletonMeta):
    def __init__(self):
        self._users = []
        self._documents = []
        self._workflows = []
        self._tasks = []
        self._search_engine = Search()
        self._access_control = AccessControl()
        self._document_analytics = DocumentAnalytics()
        self._version_control = VersionControl()

    def add_user(self, new_user: User) -> None:
        """
        Add a new user to the system.
        """
        if self._validate_user(new_user):
            self._users.append(new_user)
            print(f"User {new_user.username} added successfully.")

    def remove_user(self, user_id: int) -> bool:
        """
        Remove a user from the system.
        """

        for user_index, user in enumerate(self._users):
            if user.id == user_id:
                del self._users[user_index]
                print(f"User {user.username} removed successfully.")
                return True
        return False

    def create_document(self, title: str, content: str, author: User, document_type: DocumentTypeEnum) -> Document:
        """
        Create a new document in the system.
        """
        new_document = Document(title, content, author, document_type)
        self._documents.append(new_document)
        self._access_control.grant_access(document=new_document, user=author, level=AccessLevelEnum.OWNER)
        print(f"Document '{title}' created successfully.")

        # Initialize version control for the new document
        self._version_control.initialize_version_control(new_document)
        # Analyze the document and extract keywords
        self._document_analytics.analyze_document(new_document)

        return new_document

    def assign_task(self, document: Document, assignee: User, deadline: datetime) -> Task:
        """
        Assign a task to a user for a specific document.
        """
        new_task = Task(document=document, assignee=assignee, deadline=deadline)

        self._tasks.append(new_task)
        return new_task

    def generate_report(self, report_type: ReportTypeEnum, start_date: datetime, end_date: datetime) -> Report:
        report = Report(report_type=report_type, period=(start_date, end_date))
        report.generate_report(self._documents)
        return report

    def search_documents(self) -> list:
        """
        Search for documents based on a query string.
        """
        return self._search_engine.execute_search(documents=self._documents)

    def get_user_documents(self, user: User) -> List[Document]:
        """
        Get all documents associated with a user.
        """
        return [doc for doc in self._documents if user in doc.access_control]

    def _validate_user(self, new_user: User) -> bool:
        """
        Validate the user object.
        """
        if not isinstance(new_user, User):
            raise TypeError("Invalid user type.")
        elif any(user.id == new_user.id for user in self._users):
            raise ValueError("User already exists.")
        elif any(user.username == new_user.username for user in self._users):
            raise ValueError("Email already exists.")
        else:
            return True

    def create_workflow(self, document_type: DocumentTypeEnum, workflow_steps: List[dict]) -> "Workflow":
        """
        Create a new workflow for a specific document type.
        """

        workflow = Workflow(document_type=document_type, workflow_steps=workflow_steps)
        self._workflows.append(workflow)
        return workflow

    def assign_workflow_to_document(self, document: Document, workflow: "Workflow", user: User) -> bool:
        """
        Assign a workflow to a document and start the workflow process.
        """

        if document not in self._documents:
            raise ValueError("Document not found in the system.")

        if workflow not in self._workflows:
            raise ValueError("Workflow not found in the system.")

        if not self._access_control.check_access(document, user, AccessLevelEnum.READ_WRITE):
            raise PermissionError(f"User {user.username} does not have permission to assign workflow.")

        document.add_history_entry(f"Workflow assigned by {user.username}.")

        return True

    def get_workflows_by_document_type(self, document_type: DocumentTypeEnum) -> List["Workflow"]:
        """
        Get all workflows for a specific document type.
        """
        return [workflow for workflow in self._workflows if workflow.document_type == document_type]

        # Document Analytics Methods

    def analyze_document(self, document: Document) -> Set[str]:
        """
        Analyzes the document and extracts keywords.
        """
        return self._document_analytics.analyze_document(document)

    def find_document_duplicates(self, document: Document) -> List[Document]:
        """
        Finds duplicate documents based on the analyzed keywords.
        """
        duplicate_ids = self._document_analytics.find_duplicates(document)
        return [doc for doc in self._documents if doc.id in duplicate_ids]

    def find_related_documents(self, document: Document) -> List[Document]:
        """
        Finds related documents based on the analyzed keywords.
        """
        related_ids = self._document_analytics.find_related_documents(document)
        return [doc for doc in self._documents if doc.id in related_ids]

    def create_branch(self, document: Document, branch_name: str, user: User) -> bool:
        """
        Create a new branch for the document.
        """
        return self._version_control.create_branch(document, branch_name, user)

    def commit_changes(self, document: Document, user: User, description: str) -> bool:
        """
        Save changes to the current active branch.
        """
        return self._version_control.commit_changes(document, user, description)

    def merge_branches(self, document: Document, source_branch: str, target_branch: str, user: User) -> Tuple[
        bool, str]:
        """
        Merge changes from one branch to another.
        """
        return self._version_control.merge_branches(document, source_branch, target_branch, user)

    def get_document_version_history(self, document: Document) -> List[Dict]:
        """
        Get the version history of a document.
        """
        return self._version_control.get_version_history(document)
