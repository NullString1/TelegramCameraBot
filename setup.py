#!/usr/bin/env python3
import os
import json
import subprocess

from shutil import copy
from configparser import ConfigParser

config = ConfigParser()

print("CamBot installation")

camPath = input("Motioneye media path (/var/lib/motioneye/Camera1): ")
motionCamAddr = input("Motion api address (http://localhost:7999/0): ")
telegramApiKey = input("Telegram bot api key: ")
adminIDs = input("Admin IDs (eg. 1234567890, 0987654321, ...): ").split(",")

while len(telegramApiKey) < 40:
    telegramApiKey = input("Telegram bot api key: ")
if camPath == "":
    camPath = "/var/lib/motioneye/Camera1"
if motionCamAddr == "":
    motionCamAddr = "http://localhost:7999/0"
adminIDs = list(map(int, adminIDs))

config["settings"] = {
    "cam_path": camPath,
    "motion_cam_addr": motionCamAddr,
    "telegram_api_key": telegramApiKey
}

try:
    os.mkdir("/var/lib/cambot")
except FileExistsError:
    pass
except PermissionError:
    print("Cannot create config directory (/var/lib/cambot). Are you running as root?")
    os._exit(1)

if os.access("/var/lib/cambot/", os.W_OK):
    with open("/var/lib/cambot/cambot.conf", "w") as config_file:
        config.write(config_file)
    with open("/var/lib/cambot/ids.json", "w") as ids_file:
        ids = {"userIDs": adminIDs, "adminIDs": adminIDs}
        ids_file.write(json.dumps(ids))
    if os.access("/usr/local/bin/", os.W_OK):
        copy(os.path.abspath(os.path.dirname(__file__))+"/bot.py", "/usr/local/bin/cambot.py")
        if os.access("/etc/systemd/system/", os.W_OK):
            copy(os.path.abspath(os.path.dirname(__file__))+"/cambot.service", "/etc/systemd/system/cambot.service")
            subprocess.run("systemctl enable cambot.service".split())
            print("Installation succeeded. Restart required.")
else:
    print("Cannot access config directory (/var/lib/cambot). Are you running as root?")
    os._exit(1)
