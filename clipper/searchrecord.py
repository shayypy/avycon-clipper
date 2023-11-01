from __future__ import annotations
import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .types.playback import SearchRecord as SearchRecordPayload

    from .channel import Channel

__all__ = ("SearchRecord",)

class SearchRecord:
    __slots__ = (
        "id",
        "channel_id",
        "channel",
        "start",
        "end",
        "type",
        "mode",
        "event_id",
        "size",
    )

    def __init__(self, *, data: SearchRecordPayload, channel: Channel) -> None:
        self.id: int = data["record_id"]
        self.channel_id: str = data["channel"]
        self.channel: Channel = channel

        [month, day, year] = data["start_date"].split("/")
        [hour, minute, second] = data["start_time"].split(":")
        self.start = datetime.datetime(
            int(year), int(month), int(day),
            int(hour), int(minute), int(second),
        )
        [month, day, year] = data["end_date"].split("/")
        [hour, minute, second] = data["end_time"].split(":")
        self.end = datetime.datetime(
            int(year), int(month), int(day),
            int(hour), int(minute), int(second),
        )

        self.event_id: int = data["disk_event_id"]
        self.size: int = data["size"]
        self.type: int = data["record_type"]
        self.mode: str = data["stream_mode"]

    def __repr__(self) -> str:
        return f"<SearchRecord id={self.id!r} start={self.start!r} end={self.end!r} channel={self.channel!r} >"
