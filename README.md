# TelegramCameraBot
Telegram bot built with python-telegram-bot allowing commands which return security camera footage.

# Installation steps
1. Clone the repository `git clone https://github.com/NullString1/TelegramCameraBot`
2. Install python3. `sudo apt update && sudo apt install -y python3 python3-pip`
3. Install motioneye. See https://github.com/ccrisan/motioneye/wiki/Installation.
4. Install python-telegram-bot `pip install python-telegram-bot --upgrade`
5. Install dependencies. `sudo pip install --upgrade glob requests psutil`
6. Create a telegram bot.
   1. Start a conversation with `@BotFather`
   2. Create a bot and follow prompts `/newbot`
   3. Copy HTTP API token/key
7. Get your chat id
   1. Start a conversation with `@JsonDumpBot`
   2. Copy id under chat
8. Run setup.py as root to install cambot. `sudo python3 setup.py`  - Note: Root is required to install as systemd service and to write to certain directories.
   1. Configure path or leave default `(/var/lib/motioneye/Camera1)`
   2. Configure motion api address or leave default `(http://localhost:7999/0)`
   3. Configure telegram bot api key/token
   4. Configure adminIDs. If multiple use a comma seperated list. `eg. 1234567890,0987654321`. Note users and admins can be added later.
   5. You should see `Installation succeeded. Restart required.`
   6. Restart the device

# Usage
| Command | Alt | Alt | Usage | Admin Only? |
| ------- | ----| --- | ----- | ----------- |
| video | last | clip | sends last recorded motion clip | &cross; |
| now | pic | clipp | send picture of current scene | &cross; |
| sel i | | | sends last i video `eg sel 1 or sel 5` | &cross; |
| users ||| lists users | &cross; |
| admins ||| lists admins | &cross; |
| kill | stop || kills the bot | &check; |
| addUser ||| adds a new user | &check; |
| addAdmin ||| adds a new admin | &check; |

Note: When adding an admin, ensure they are also added as a user

# Configuration files
- `ids.json` - `/var/lib/cambot/ids.json`
- `cambot.conf` - `/var/lib/cambot/cambot.conf`
# Script
- `cambot.py` - `/usr/local/bin/cambot.py`
- `cambot.service` - `/etc/systemd/system/cambot.service`
# Logs
- `systemctl status cambot`
- `tail -f /var/log/cambot.log`
