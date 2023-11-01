from __future__ import annotations
import datetime
from typing import List

from .channel import Channel
from .http import HTTP
from .searchrecord import SearchRecord


__all__ = (
    'AvyClient',
)

class AvyClient:
    def __init__(self, base_url: str) -> None:
        self.http = HTTP(base_url)

    async def login(self, username: str, password: str) -> None:
        await self.http.init(username, password)

    async def close(self) -> None:
        if self.http.session and not self.http.session.closed:
            await self.http.session.close()

    async def fetch_channels(self) -> List[Channel]:
        data = await self.http.get_channel_info()
        return [
            Channel(data=channel_data)
            for channel_data in
            data["channel_param"]["items"]
        ]

    async def search_records(
        self,
        channels: List[Channel],
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> List[SearchRecord]:
        data = await self.http.search_records(
            [c.id for c in channels],
            start=start,
            end=end,
        )
        return [
            SearchRecord(
                data=record_data,
                channel=next(c for c in channels if c.id == record_data["channel"])
            )
            for record_data in
            data
        ]
