from fastapi import HTTPException, status
from constants.errors import GroupErrors

class GroupError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class GroupNotFoundError(GroupError):
    def __init__(self, group_name: str):
        super().__init__(GroupErrors.NOT_FOUND.format(group_name=group_name), 404)

class GroupListError(GroupError):
    def __init__(self, error: str):
        super().__init__(GroupErrors.LIST_ERROR.format(error=error), 500)

class GroupCreateError(GroupError):
    def __init__(self, error: str):
        super().__init__(GroupErrors.CREATE_ERROR.format(error=error), 500)

class GroupAddUserError(GroupError):
    def __init__(self, error: str):
        super().__init__(GroupErrors.ADD_USER_ERROR.format(error=error), 500)

class GroupGetUsersError(GroupError):
    def __init__(self, error: str):
        super().__init__(GroupErrors.GET_USERS_ERROR.format(error=error), 500) 