from typing import Any


class ExpiredException(Exception):
    pass

class UnknownException(Exception):
    pass

class NotFoundException(Exception):
    pass

class UnauthorizedException(Exception):
    pass

class AlreadyExistsError(Exception):
    pass

class RequestSpecificError(Exception):
    def __init__(self, error_type: str, error_msg: str) -> None:
        self.error_type = error_type
        self.error_msg = error_msg

        self.msg = f"{error_type} - {error_msg}"
        super().__init__(self.msg)

class ResponseException(Exception):
    def __init__(self, msg: str, data: Any) -> None:
        self.data = data
        self.msg = msg
        super().__init__(msg + " (Response Data can be accesed with exception.data)")