from typing import List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from models.document import Document
    from models.user import User


class Department:
    def __init__(self, name: str, head: Union['User', None], members: List['User'] = None) -> None:
        if members is None:
            members = []

        self.name = name
        self.head = head
        self.members = [head] + members

    def add_member(self, user: 'User') -> None:
        """
        Add a new member to the department.
        """
        self.members.append(user)

    def remove_member(self, user: 'User') -> None:
        """
        Remove a member from the department.
        """
        if user in self.members:
            self.members.remove(user)
        else:
            raise ValueError(f"{user.username} is not a member of this department.")

    def get_all_members_documents(self) -> List['Document']:
        """
        Get a list of all documents created by members of the department.
        """

        documents = []
        for member in self.members:
            documents.extend(member.documents)
        return documents
