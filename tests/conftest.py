import pytest

from enums import PositionEnum, AccessLevelEnum, DocumentTypeEnum
from models.department import Department
from models.document import Document
from models.user import User


@pytest.fixture
def user_data():
    return {
        'username': 'test_user',
        'password': 'password123',
        'position': PositionEnum.MANAGER,
        'access_level': AccessLevelEnum.ADMIN
    }


@pytest.fixture
def department_data():
    return {
        'name': 'Test Department'
    }


@pytest.fixture
def user(user_data):
    user = User(
        username=user_data['username'],
        password=user_data['password'],
        position=user_data['position'],
        department=None,  # Изначально без отдела
        access_level=user_data['access_level'],
    )
    return user


@pytest.fixture
def department(department_data, user):
    department = Department(
        name=department_data['name'],
        head=user,
    )
    user.department = department
    return department


@pytest.fixture
def document(user):
    return Document(
        title="Test Document",
        content="Test content",
        author=user,
        document_type=DocumentTypeEnum.CONTRACT
    )
