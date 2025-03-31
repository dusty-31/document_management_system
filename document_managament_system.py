from datetime import datetime
from typing import List

from models.access_control import AccessControl
from models.document import Document
from enums import AccessLevelEnum, ReportTypeEnum
from models.report import Report
from models.search import Search
from models.task import Task
from models.user import User


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

    def create_document(self, title: str, content: str, author: User) -> Document:
        """
        Create a new document in the system.
        """
        new_document = Document(title, content, author)
        self._documents.append(new_document)
        self._access_control.grant_access(document=new_document, user=author, level=AccessLevelEnum.OWNER)
        print(f"Document '{title}' created successfully.")
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
        report.generate_report(self._documents, self._users)
        return report

    def search_documents(self, query: str) -> list:
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
