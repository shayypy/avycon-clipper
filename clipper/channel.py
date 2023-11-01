from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .types.channel import Channel as ChannelPayload

__all__ = ("Channel",)

class Channel:
    __slots__ = (
        "id",
        "status",
        "name",
        "alias",
        "abilities",
        "intelligent_abilities",
        "alarm_in_num",
        "alarm_out_num",
        "video_loss",
    )

    def __init__(self, *, data: ChannelPayload) -> None:
        self.id: str = data["channel"]
        self.status = data["connect_status"]
        self.name: str = data["channel_name"]
        self.alias: str = data["channel_alias"]
        self.abilities: List[str] = data.get("ability") or []
        self.intelligent_abilities: List[str] = data.get("intelligent_ability") or []
        self.alarm_in_num: int = data.get("alarm_in_num") or 0
        self.alarm_out_num: int = data.get("alarm_out_num") or 0
        self.video_loss: bool = data.get("videoloss") or False

    def __repr__(self) -> str:
        return f"<Channel id={self.id!r} alias={self.alias!r} name={self.name!r} >"

    @property
    def hls_live_path(self) -> str:
        return f"/hls/live/{self.id}/1/livetop.mp4"
