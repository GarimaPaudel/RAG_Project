from http import HTTPStatus
from fastapi import HTTPException, status


class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str | None = None,
    ):
        if not detail:
            detail = HTTPStatus(status_code).description
        super().__init__(status_code=status_code, detail=detail)

