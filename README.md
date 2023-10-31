## Setup

Create a file named `.env` and populate it like so, replacing the values in quotes:

```
AVYCON_ADDRESS="http://192.168.1.123"
AVYCON_USERNAME="username"
AVYCON_PASSWORD="password"
AVYCON_CHANNEL_ID="CH1"
```

Note that the user you use should only have "Manual Record" permissions, as well as backup, live, and playback for the camera you selected. It will also need "Remote Login" if you are not running this on your own network. It should never be an admin user.
