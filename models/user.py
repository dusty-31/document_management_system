from typing import Union

from enums import PositionEnum, AccessLevelEnum
from models.department import Department


class User:
    global_user_id = 0

    def __init__(
            self,
            username: str,
            password: str,
            position: PositionEnum,
            department: Union[Department, None],  # None if not assigned to a department
            access_level: AccessLevelEnum,
    ) -> None:
        self.id = self._get_user_id()
        self.username = username
        self.password = password
        self.position = position.value
        self.department = department
        self.access_level = access_level
        self.documents = list()

    def _get_user_id(self) -> int:
        """
        Get a unique user ID from class variable.
        """

        self.global_user_id += 1
        return self.global_user_id

    def authenticate(self, password: str) -> bool:
        """
        Authenticate the user with the provided password.
        """

        return self.password == password

    def change_access_level(self, new_access_level: AccessLevelEnum) -> None:
        """
        Change the access level of the user.
        """

        self.access_level = new_access_level
