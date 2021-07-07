#!/usr/bin/env python3
import logging
import glob
import os
import requests
import time
import psutil
import json

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, UpdateFilter
from configparser import ConfigParser

path = "/var/lib/cambot/"

config = ConfigParser()
config.read(path + "cambot.conf")

settings = config["settings"]

camPath = settings["cam_path"]+"/*/"
motion_cam_addr = settings["motion_cam_addr"]
telegram_api_key = settings["telegram_api_key"]

adminIDs = []
userIDs = []

with open(path+"ids.json", "r") as f:
    data=json.loads(f.read())
    for user in data["adminIDs"]:
        adminIDs.append(user)
    for user in data["userIDs"]:
        userIDs.append(user)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log = logging.FileHandler("/var/log/cambot.log")
log.setLevel(logging.INFO)
lformat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log.setFormatter(lformat)
logger.addHandler(log)
stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
stream.setFormatter(lformat)
logger.addHandler(stream)

def writeIDs():
    global userIDs, adminIDs
    ids = {"userIDs": userIDs, "adminIDs": adminIDs}
    with open(path+"ids.json", "w") as f:
        f.write(json.dumps(ids))

def getLast(s):
    global camPath
    return(max(glob.iglob(camPath + s),key=os.path.getctime))

class text_args_f(UpdateFilter):
    def __init__(self, text: str):
        self.text = text

    def filter(self, update):
        if update.message.text.lower().find(self.text.lower()) != -1:
            if len(update.message.text.split(self.text)) == 2:
                return True
        return False

def restricted(uids):
    def wrapper(func):
        def wrapped(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id not in uids:
                print("Unauthorized access denied for {}.".format(user_id))
                update.message.reply_text("You do not have permission to run this command")
                return
            return func(update, context, *args, **kwargs)
        return wrapped
    return wrapper

def has_handle(fpath):
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if fpath == item.path:
                    return True
        except Exception:
            pass

    return(False)

def log(user, message):
    logger.info(f"{user.id} ({user.username}) - {message}")

@restricted(userIDs)
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
"""
video / last  / clip - sends last clip
now / pic / clipp - sends picture of current scene
sel (i) - sends last i video
users - lists users
admins - lists admins
addUser (id) - adds a new user with id (ADMINS only)
addAdmin (id) - adds a new admin with id (ADMINS only)
kill / stop - stops the bot (ADMINS ONLY)""")

@restricted(adminIDs)
def addUser(update: Update, context: CallbackContext) -> None:
    global userIDs
    id=update.message.text.split("addUser")[1]
    if id.strip().isdigit():
        id=int(id)
    if id not in userIDs:
        userIDs.append(id)
        writeIDs()
        log(update.effective_user, f"Added new user {id}")
        update.message.reply_text(f"Added new user {id}")
    else:
        log(update.effective_user, f"User already exists {id}")
        update.message.reply_text(f"User already exists {id}")

@restricted(adminIDs)
def addAdmin(update: Update, context: CallbackContext) -> None:
    global adminIDs
    id=update.message.text.split("addAdmin")[1]
    if id.strip().isdigit():
        id=int(id)
    adminIDs.append(id)
    writeIDs()
    log(update.effective_user, f"Added new admin {id}")
    update.message.reply_text(f"Added new admin {id}")

@restricted(adminIDs)
def restart_command(update: Update, context: CallbackContext) -> None:
    os._exit(0)

@restricted(userIDs)
def selclip_command(update: Update, context: CallbackContext) -> None:
    global camPath
    i=update.message.text.split("sel")[1]
    if i.strip().isdigit():
        i=int(i)
    vid=sorted(glob.iglob(camPath+"*.mp4"), key=os.path.getctime)[0-i]
    update.message.reply_video(open(vid, "rb"), caption=f"Video {i}")
    log(update.effective_user, f"Sent clip {i} from {vid}")

@restricted(userIDs)
def video_command(update: Update, context: CallbackContext) -> None:
    path=getLast("*.mp4")
    update.message.reply_video(open(path, "rb"), caption="Last video")
    log(update.effective_user, f"Sent last video: {path}")

@restricted(userIDs)
def now_command(update: Update, context: CallbackContext) -> None:
    requests.get(motion_cam_addr + "/action/snapshot")
    time.sleep(0.1)
    path=getLast("*snap.jpg")
    while has_handle(path):
        time.sleep(0.05)
        logger.debug(f"{path} has handle.")
    update.message.reply_photo(open(path, "rb"), caption="Snapshot")
    log(update.effective_user, f"Sent snapshot: {path}")

@restricted(userIDs)
def users_command(update: Update, context: CallbackContext) -> None:
    global userIDs
    update.message.reply_text(f"userIDs: {userIDs}")
    log(update.effective_user, f"Sent users list")

@restricted(userIDs)
def admins_command(update: Update, context: CallbackContext) -> None:
    global adminIDs
    update.message.reply_text(f"adminIDs: {adminIDs}")
    log(update.effective_user, f"Sent admins list")

def start_command(update: Update, context: CallbackContext) -> None:
    global adminIDs
    for admin in adminIDs:
        update.message.bot.sendMessage(admin, f"User {update.effective_user.id} requests to join")

def main() -> None:
    updater = Updater(telegram_api_key)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("start", start_command))

    dispatcher.add_handler(MessageHandler(Filters.text(["video", "last", "clip", "Video", "Last", "Clip"]), video_command))
    dispatcher.add_handler(MessageHandler(Filters.text(["now", "pic", "clipp", "Now", "Pic", "Clipp"]), now_command))
    dispatcher.add_handler(MessageHandler(Filters.text(["users"]), users_command))
    dispatcher.add_handler(MessageHandler(Filters.text(["admins"]), admins_command))
    dispatcher.add_handler(MessageHandler(Filters.text(["kill", "stop", "restart", "reboot", "reload"]), restart_command))
    dispatcher.add_handler(MessageHandler(text_args_f(text="sel"), selclip_command))
    dispatcher.add_handler(MessageHandler(text_args_f(text="addUser"), addUser))
    dispatcher.add_handler(MessageHandler(text_args_f(text="addAdmin"), addAdmin))

    logger.info("Started.")

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
