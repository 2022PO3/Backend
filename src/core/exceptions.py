class OriginValidationException(Exception):
    """
    Exception raised when there is an error in the origin validation of the request.
    """

    def __init__(self, message: str, status_code: int) -> None:
        self.status = status_code
        super().__init__(message)


class BackendException(Exception):
    """
    Generic exception class which indicates errors happening in the Backend.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DeletionException(Exception):
    """
    Exception thrown when an object cannot be deleted due to foreign key relationships.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
