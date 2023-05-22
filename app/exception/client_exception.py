from werkzeug.exceptions import HTTPException


class ClientError(HTTPException):
    """ClientError exception class inherits the :class:`HTTPException` class to handle
    client side exceptions of the Web Crawler application.
    """

    def __init__(self, message, status_code=400):
        self.code = status_code
        super().__init__(description=message)
