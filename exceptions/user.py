from fastapi import HTTPException, status
from constants.errors import UserErrors

class UserError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class UserNotFoundError(UserError):
    def __init__(self, user_id: str):
        super().__init__(UserErrors.NOT_FOUND.format(user_id=user_id), 404)

class UserListError(UserError):
    def __init__(self, error: str):
        super().__init__(UserErrors.LIST_ERROR.format(error=error), 500)

class UserCreateError(UserError):
    def __init__(self, error: str):
        super().__init__(UserErrors.CREATE_ERROR.format(error=error), 500)

class UserUpdateError(UserError):
    def __init__(self, error: str):
        super().__init__(UserErrors.UPDATE_ERROR.format(error=error), 500)

class UserDeleteError(UserError):
    def __init__(self, error: str):
        super().__init__(UserErrors.DELETE_ERROR.format(error=error), 500)

class UserRoleError(UserError):
    def __init__(self, error: str):
        super().__init__(UserErrors.ROLE_ERROR.format(error=error), 500) 