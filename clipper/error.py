from __future__ import annotations

from typing import TYPE_CHECKING
import aiohttp

from .util import error_code_map

if TYPE_CHECKING:
    from .types.api import BadResponse


class AvyconAPIException(Exception):
    def __init__(self, response: aiohttp.ClientResponse, data: BadResponse) -> None:
        self.response = response
        self.data = data
        self.message = error_code_map.get(data["error_code"]) if data.get("error_code") else None
        super().__init__(f"[{response.status}]: {self.message} ({data})")
