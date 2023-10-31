import asyncio
import os
import clipper
from dotenv import load_dotenv
load_dotenv()

host = os.environ.get("AVYCON_ADDRESS")
username = os.environ.get("AVYCON_USERNAME")
password = os.environ.get("AVYCON_PASSWORD")
channel = os.environ.get("AVYCON_CHANNEL_ID")
if any([x is None for x in [host, username, password, channel]]):
    raise ValueError("Missing a required environment variable.")

async def main():
    client = clipper.AvyClient(host)
    await client.login(username, password)
    print(await client.fetch_channels())

if __name__ == "__main__":
    asyncio.run(main())
