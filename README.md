# AVYCON DVR Clipper

Creates a clip of the last 2 minutes (default) for a specific channel then saves it to a directory on the local machine. Clips are named as follows: ``directory/CameraName-YY-MM-DDTHH-MM-SS.mp4``. There is no audio.

## Setup

Create a file named `.env` and populate it like so, replacing the values in quotes:

```py
AVYCON_ADDRESS="http://192.168.1.123"
AVYCON_USERNAME="username"
AVYCON_PASSWORD="password"
AVYCON_CHANNEL_ID="CH1"
# All below are optional
CLIP_DIRECTORY="/home/user/clips"
CLIP_SECONDS="120"
```

You should create a new user for this program with the "Remote Login" permission, as well as the "Playback" permission for the camera you selected. It should _not_ be an admin user. Clips are saved without audio, so the Audio permission is not needed. Your policy for this user should look like this:

![image](https://github.com/shayypy/avycon-clipper/assets/43248357/efb55ba7-40c8-41c5-a772-62dbe0c04daf)

## Usage

```bash
python3 main.py
```
