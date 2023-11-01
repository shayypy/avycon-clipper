from __future__ import annotations

import asyncio
import datetime
import os
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
import clipper
from clipper.error import AvyconAPIException
from yt_dlp import YoutubeDL, utils
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get("AVYCON_ADDRESS")
username = os.environ.get("AVYCON_USERNAME")
password = os.environ.get("AVYCON_PASSWORD")
channel_id = os.environ.get("AVYCON_CHANNEL_ID")
clip_dir = os.environ.get("CLIP_DIRECTORY") or "clips"
clip_secs = int(os.environ.get("CLIP_SECONDS") or 120)
if host is None or username is None or password is None or channel_id is None:
    raise ValueError("Missing a required environment variable.")

client = clipper.AvyClient(host)


async def main():
    await client.login(username, password)
    channels = await client.fetch_channels()
    channel = next((c for c in channels if c.id == channel_id), None)
    if not channel:
        raise ValueError(f"Channel with ID {channel_id} not found.")

    # This may encounter issues when the DVR and local
    # machine are not in the same timezone.
    now = datetime.datetime.now()
    start = now - datetime.timedelta(seconds=clip_secs)

    # records = await client.search_records(
    #     [channel],
    #     start=start,
    #     end=now,
    # )
    # if not records:
    #     raise ValueError(
    #         f"No records found during the last {clip_secs} seconds. Is your DVR always recording?"
    #     )

    # record = records[-1]

    urls = await client.http.get_playback_url()
    parsed = urlparse(urls["mpd"])
    params = parse_qs(parsed.query)
    # stream_id = params["id"][0]
    parsed = parsed._replace(
        query=urlencode(
            {
                **{k: params[k][0] for k in params},
                "chn": int(channel.id.replace("CH", "")) - 1,
                "streamtype": "1",
                "recordtype": "1",  # "4294967295",
                "skip_i": "0",
                "s": start.strftime("%Y%m%d%H%M%S"),
                "e": now.strftime("%Y%m%d235959"),
            }
        )
    )
    # init_path = urlunparse(
    #     (
    #         "",
    #         "",
    #         "/API/PlayBack/Dash/video/init.mp4",
    #         "",
    #         f"id={stream_id}&seg=0",
    #         "",
    #     )
    # )
    ydl_opts = {
        "format": "mp4/bestvideo",
        "outtmpl": f"{clip_dir}/{channel.name}-{start.strftime('%Y-%m-%dT%H-%M-%S')}.mp4",
    }
    utils.std_headers["Authorization"] = "Basic Og==" # type: ignore
    utils.std_headers["Cookie"] = f"session={client.http.cookie}" # type: ignore
    utils.std_headers["X-csrftoken"] = client.http.csrf_token # type: ignore

    for tries in range(0, 5):
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([host + parsed.geturl()])
        except utils.DownloadError:
            # if (
            #     isinstance(e, AvyconAPIException)
            #     and e.data.get("reason") == "playback_mutex"
            # ):
            #     print(
            #         f"Playback already in progress, trying again in 5s (attempt {tries + 1})"
            #     )
            print(f"Failed, trying again in 5s (attempt {tries + 1})")
            await asyncio.sleep(5)
            continue
            # raise
        else:
            break


async def wrapper():
    try:
        await main()
    except:
        await client.close()
        raise
    else:
        await client.close()


if __name__ == "__main__":
    asyncio.run(wrapper())
