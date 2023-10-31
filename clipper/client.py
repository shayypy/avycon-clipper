from __future__ import annotations
from typing import List

from .channel import Channel
from .http import HTTP


__all__ = (
    'AvyClient',
)

class AvyClient:
    def __init__(self, base_url: str) -> None:
        self.http = HTTP(base_url)

    async def login(self, username: str, password: str) -> None:
        await self.http.init(username, password)

    async def fetch_channels(self) -> List[Channel]:
        data = await self.http.get_channel_info()
        return [
            Channel(data=channel_data)
            for channel_data in
            data["channel_param"]["items"]
        ]
