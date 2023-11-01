from __future__ import annotations
from typing import List, TypedDict


class IdKey(TypedDict):
    id: str
    key: str


class GetPrivateKey(TypedDict):
    id_keys: List[IdKey]


class GetPlaybackUrl(TypedDict):
    mpd: str
    keepalive: str
    stop: str


class SearchRecord(TypedDict):
    channel: str
    stream_mode: str
    record_type: int
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    record_id: int
    disk_event_id: int  # 0 if no event
    size: int  # bytes
