from werkzeug.exceptions import HTTPException


class ClientError(HTTPException):
    def __init__(self, message, status_code=400):
        self.code = status_code
        super().__init__(description=message)
