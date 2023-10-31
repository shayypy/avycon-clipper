from typing import Any, Dict, Literal, NotRequired, TypedDict, Union


class SuccessResponse(TypedDict):
    result: Literal["success"]
    data: NotRequired[Dict[str, Any]]


class FailureResponse(TypedDict):
    result: Literal["failed"]
    reason: str


class InvalidResponse(TypedDict):
    version: str
    error_code: str


BadResponse = Union[FailureResponse, InvalidResponse]
