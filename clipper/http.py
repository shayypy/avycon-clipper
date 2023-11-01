from __future__ import annotations

import datetime
import hashlib

import json as j
import re
import secrets
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import aiohttp

from .error import AvyconAPIException

if TYPE_CHECKING:
    from .types.api import SuccessResponse
    from .types.channel import GetChannelInfo
    from .types.playback import GetPlaybackUrl, GetPrivateKey, SearchRecord

__all__ = ("HTTP",)


def now_query() -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d@%H:%M:%S")


class HTTP:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.cookie: Optional[str] = None
        self.csrf_token: Optional[str] = None
        self.nonce_count = 1

    async def init(self, username: str, password: str) -> SuccessResponse:
        self.session = aiohttp.ClientSession(self.base_url)
        uri = "/API/Web/Login"

        # https://en.wikipedia.org/wiki/Digest_access_authentication
        # AVYCON uses digest auth. Some endpoints _seem_ to
        # accept basic, but it does not work for logging in.

        # https://github.com/aio-libs/aiohttp/pull/2213
        # aiohttp does not support this natively (unlike requests)
        # We could make this a sync application and use requests
        # but I decided to just implement it manually

        # 401
        bad_response = await self.session.post(uri)
        bad_response_body = await bad_response.text()
        www_authenticate = bad_response.headers.get("WWW-Authenticate")
        if not www_authenticate:
            raise ValueError("Missing WWW-Authenticate header from server.")

        # Thanks https://stackoverflow.com/a/1349528
        reg = re.compile(r'(\w+)[=] ?"?(\w+)"?')
        parsed = dict(reg.findall(www_authenticate))

        method = "POST"
        realm: str = parsed["realm"]
        qop: Optional[str] = parsed.get("qop")
        nonce: str = parsed["nonce"]
        cnonce = secrets.token_urlsafe()

        b = lambda string: string.encode(encoding="UTF-8")

        ha1 = hashlib.md5(b(f"{username}:{realm}:{password}")).hexdigest()
        ha2 = hashlib.md5(
            b(
                f"POST:{uri}:{hashlib.md5(b(bad_response_body)).hexdigest()}"
                if qop == "auth-int"
                else f"POST:{uri}"
            )
        ).hexdigest()
        response_val = hashlib.md5(
            b(
                f"{ha1}:{nonce}:{self.nonce_count}:{cnonce}:{qop}:{ha2}"
                if qop == "auth" or qop == "auth-int"
                else f"{ha1}:{nonce}:{ha2}"
            )
        ).hexdigest()

        digest_header = (
            "Digest "
            f'username="{username}", '
            f'realm="{realm}", '
            f'nonce="{nonce}", '
            f'uri="{uri}", '
            f'response="{response_val}", '
            f"qop={qop}, "
            f"nc={self.nonce_count}, "
            f'cnonce="{cnonce}"'
        )
        response = await self.session.request(
            method,
            uri,
            headers={
                "Authorization": digest_header,
            },
            json={
                "data": {
                    "remote_terminal_info": "WEB,firefox",
                },
            },
        )
        text = await response.text()
        if not response.ok:
            raise ValueError(
                f"Failed to log in with username {username}: [{response.status}] {text}"
            )

        self.nonce_count += 1
        self.username = username
        self.password = password
        cookie = response.cookies.get("session")
        if cookie:
            self.cookie = cookie.value
        self.csrf_token = response.headers.get("X-csrftoken")
        return j.loads(text)

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if not self.session:
            raise ValueError("Missing session, call `.init` first.")

        headers = headers or {}
        body = None

        headers["Authorization"] = "Basic Og=="
        if self.cookie:
            headers["Cookie"] = f"session={self.cookie}"
        if self.csrf_token:
            headers["X-csrftoken"] = self.csrf_token

        if json:
            headers["Content-Type"] = "application/json"
            body = j.dumps(json)

        if body is None and method == "POST":
            headers["Content-Type"] = "application/json"
            body = "{}"

        response = await self.session.request(
            method,
            path,
            headers=headers,
            data=body,
            params={
                now_query(): "",
            }
        )
        if response.content_type == "application/json":
            data = await response.json()
        else:
            data = response._body

        if not response.ok:
            raise AvyconAPIException(response, data)

        return data

    async def logout(self) -> SuccessResponse:
        return await self.request(
            "POST", "/API/Web/Logout",
            json={
                "data": {},
                "version": "1.0",
            },
        )

    async def create_heartbeat(self) -> SuccessResponse:
        return await self.request(
            "POST", "/API/Login/Heartbeat",
            json={
                "actionType": "create",
                "data": {},
                "version": "1.0",
            }
        )

    async def get_channel_info(self) -> GetChannelInfo:
        data = await self.request(
            "POST", "/API/Login/ChannelInfo/Get"
        )
        return data["data"]

    async def search_records(
        self,
        channel_ids: List[str],
        *,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> List[SearchRecord]:
        data = await self.request(
            "POST", "/API/Playback/SearchRecord/Search",
            json={
                "version": "1.0",
                "data": {
                    "channel": channel_ids,
                    "enable_smart_search": 0,
                    # "record_type": 262145,  # normal, manual
                    "record_type": 1,  # normal
                    "smart_region": [],
                    "stream_mode": "Substream",
                    "start_date": start.strftime("%m/%d/%Y"),
                    "start_time": start.strftime("%H:%M:%S"),
                    "end_date": end.strftime("%m/%d/%Y"),
                    "end_time": end.strftime("%H:%M:%S"),
                },
            },
        )
        return data["data"]["record"][0]

    async def get_private_key(self) -> GetPrivateKey:
        return await self.request(
            "POST", "/API/Web/Get_Private_Key",
            json={
                "number": 1,
            }
        )

    async def get_playback_url(self) -> GetPlaybackUrl:
        now = int(datetime.datetime.now().timestamp() * 1000)
        data = await self.request(
            "POST", f"/API/GetDashPlaybackUrl?{now}="
        )
        return data["data"]
