from __future__ import annotations

from typing import List, Literal, TypedDict


class Channel(TypedDict):
    channel: str
    connect_status: Literal["Online", "NotConfigured"]
    channel_name: str
    channel_alias: str
    ability: List[str]
    intelligent_ability: List[str]
    alarm_in_num: int
    alarm_out_num: int
    videoloss: bool


class GetChannelInfo(TypedDict):
    channel_param: ChannelParam


class ChannelParam(TypedDict):
    type: Literal["array"]
    min_size: int
    max_size: int
    items: List[Channel]
