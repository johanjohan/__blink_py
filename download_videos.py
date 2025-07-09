"""
    based on
    https://github.com/fronzbot/blinkpy

    asks for code which comes via SMS or call
    downloads all your videos from the Blink server
    
    2024 11 11 - 3j
        cleanup
        secure_delete
    
"""
# NOTE 3j: also changed blinkpy.py to add a ansi-colored logger

import asyncio
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
import os
import logging
import shutil
from datetime import datetime
import pytz
import blinkpy.helpers.util as bhutil
import art
import colorama 
from colorama import Fore, Back, Style
from sortedcontainers import SortedSet
import time
from tqdm import tqdm
import util
from secure_delete import secure_delete
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()  # hide main window

# ------------------------------------------------
# | custom logger
# ------------------------------------------------
class CustomFormatter(logging.Formatter):
    #https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    level       = Fore.LIGHTBLACK_EX + '%(levelname)7s | '
    #format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = '%(message)s'

    FORMATS = {
        logging.DEBUG:      level + Fore.LIGHTBLACK_EX + format + Fore.RESET,
        logging.INFO:       level + Fore.WHITE + format + Fore.RESET,
        logging.WARNING:    level + Fore.YELLOW + format + Fore.RESET,
        logging.ERROR:      level + Fore.RED + format + Fore.RESET,
        logging.CRITICAL:   level + Style.BRIGHT + Fore.RED + format + Fore.RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # change here ALL < TRACE < DEBUG < INFO < WARN < ERROR < FATAL < OFF

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) # keep logging.DEBUG
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

# ------------------------------------------------
# | change these vars
# ------------------------------------------------
FOLDER_VIDEOS_BLINK = os.path.abspath("__blink_videos") # "../__blink_videos"

FOLDER_SECRET       = ".secret"
CREDENTIALS         = os.path.join(FOLDER_SECRET, ".blink_credentials.json") # f"{FOLDER_SECRET}/.blink_credentials.json" # "../__blink_credentials.json"

# temp paths for more secret files
PATH_SECRET_TEMP_CREDENTIALS = f"{FOLDER_VIDEOS_BLINK}/../{FOLDER_SECRET}/__temp_blink.json"
PATH_SECRET_INTERNAL_PARAMS  = f"{FOLDER_VIDEOS_BLINK}/../{FOLDER_SECRET}/homescreen.json" # all your system internals, SN#s, keep secret

# ------------------------------------------------
# | vars
# ------------------------------------------------
FOLDER_CLOUD        = "__sorted_cloud"
FOLDER_LOCAL        = "__sorted_local"

EXT                 = ".mp4"

CAMERA_NAME         = "all"
DELAY               = 2 # secs
ASCIIFONT           = 'tarty2' # thin3 isometric3 tarty2

# some debug flags
B_BLINK             = True
B_CLOUD             = True # in B_BLINK
B_SYNC              = True # in B_BLINK

B_FOLDERS           = True

# ------------------------------------------------
# | file to secure_delete
# ------------------------------------------------
FILES_TO_SECURE_DELETE = [PATH_SECRET_TEMP_CREDENTIALS]

# ------------------------------------------------
# | util
# ------------------------------------------------
def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            logger.debug(f"Directory created: {dir_path}")
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
    else:
        logger.debug(f"Directory already exists: {dir_path}")
        pass
        
def scan_directory_for_mp4(outdir, _ext=EXT):
    # Ensure the directory exists
    if not os.path.isdir(outdir):
        logger.error(f"The directory {outdir} does not exist.")
        return []

    # List all files in the directory
    files = os.listdir(outdir)

    # Filter files ending with ".mp4"
    mp4_files = [file for file in files if file.lower().endswith(_ext)]

    return mp4_files

def extract_blink_utc_datetime(filename):
    # 2-g8t1-gj01-3205-1xhg-2024-09-12t18-59-39-00-00.mp4
    # Remove the file extension
    basename = os.path.splitext(filename)[0]

    # Get the last 25 characters of the basename
    date_time_str = basename[-25:]
    camera_str = basename[:-26] # -

    # Extract date and time
    date_str = date_time_str[:10]  # "2024-09-12" # UTC
    time_str = date_time_str[11:19]  # "18-59-39-00-00"
    tz = date_time_str[19:]
    
    logger.debug(f"{camera_str}, {date_str}, {time_str}, {tz}")

    return camera_str, date_str, time_str, tz
    
def convert_utc_to_local(date_str, time_str, local_timezone_str, local_z_str):
    # Combine date and time strings into one string
    date_time_str = f"{date_str}T{time_str}"
    
    # Parse the combined string into a datetime object
    try:
        utc_dt = datetime.strptime(date_time_str, '%Y-%m-%dT%H-%M-%S')
    except ValueError as e:
        logger.error(f"Error parsing datetime: {e}")
        return None
    
    # Define UTC and local timezones
    utc_zone = pytz.utc
    local_zone = pytz.timezone(local_timezone_str)
    
    # Make the datetime object timezone-aware in UTC
    utc_dt = utc_zone.localize(utc_dt)
    
    # Convert UTC time to local time
    local_dt = utc_dt.astimezone(local_zone)
    
    #formatted_local_dt = local_dt.strftime('%Y-%m-%dT%H-%M-%S%z-%Z') # 2024-09-12T23-21-40+0200-CEST
    formatted_local_dt = local_dt.strftime('%Y-%m-%dT%H-%M-%S') + local_z_str # 2024-09-12T23-21-40+02-00
    
    return formatted_local_dt

# ------------------------------------------------
# | blink start()
# ------------------------------------------------
async def blink_start():
    
    blink = Blink()
    auth = Auth(await bhutil.json_load(CREDENTIALS))
    blink.auth = auth
    await blink.start()
    
    status = await blink.get_status() # notification status 
    print()
    print("notification status:", bhutil.json_dumps(status))
    
    """
    Download all videos from server since specified time.

    :param path: Path to write files.  /path/<cameraname>_<recorddate>.mp4
    :param since: Date and time to get videos from.
              Ex: "2018/07/28 12:33:00" to retrieve videos since
              July 28th 2018 at 12:33:00
    :param camera: Camera name to retrieve.  Defaults to "all".
               Use a list for multiple cameras.
    :param stop: Page to stop on (~25 items per page. Default page 10).
    :param delay: Number of seconds to wait in between subsequent video downloads.
    :param debug: Set to TRUE to prevent downloading of items.
              Instead of downloading, entries will be printed to log.
    """
    if B_CLOUD:
        #logger.info(f"\n{Fore.CYAN}{art.text2art("save cloud", font=ASCIIFONT)}")
        util.logo("save cloud")
        create_dir_if_not_exists(FOLDER_VIDEOS_BLINK)
        logger.info(f"saving videos to {Fore.MAGENTA}{FOLDER_VIDEOS_BLINK}{Fore.RESET}\n")
        
        await blink.download_videos(
            path=FOLDER_VIDEOS_BLINK, 
            camera=CAMERA_NAME,
            since="2024/01/01 00:00", 
            stop=1000, 
            delay=DELAY
        ) 
    

    # from blinksync.py - save secret internals, just for info...
    await blink.save(PATH_SECRET_TEMP_CREDENTIALS) # OK!!!
    
    #await util.json_dumps(blink.homescreen)
    await bhutil.json_save(blink.homescreen, PATH_SECRET_INTERNAL_PARAMS) # all your internal blink params

    # ------------------------------------------------
    # | sync module: dl local files from usb
    # ------------------------------------------------
    if B_SYNC:
        #logger.info(f"\n{Fore.CYAN}{art.text2art("save sync", font=ASCIIFONT)}")
        util.logo("save sync")
        logger.debug(f"Sync status: {blink.network_ids}")
        logger.debug(f"Sync len: {len(blink.networks)}")   
        logger.info(f"Sync: {blink.networks}")   
        
        logger.info(f"saving videos to {Fore.MAGENTA}{FOLDER_LOCAL}{Fore.RESET}\n")
        
        #assert len(blink.networks) > 0
        if not len(blink.networks) > 0:
            logger.error(f"NO Sync networks:  len(blink.networks): {len(blink.networks)}")  
        else:
            my_sync: BlinkSyncModule = blink.sync[
                blink.networks[list(blink.networks)[0]]["name"]
            ]       
            
            _b_verbose = False 

            # verbose cams
            if _b_verbose:
                logger.debug("listing cameras:")
                for name, camera in blink.cameras.items():
                    logger.debug(f"name: {name}\ncamera.attribute: {camera.attributes}\n")

            # local storage
            my_sync._local_storage["manifest"] = SortedSet()
            await my_sync.refresh()
            
            # verbose _local_storage
            if _b_verbose:
                if my_sync.local_storage and my_sync.local_storage_manifest_ready:
                    logger.debug(f"{Fore.GREEN}Manifest is ready{Fore.RESET}")
                    logger.debug(f"Manifest {Fore.CYAN}{my_sync._local_storage['manifest']}{Fore.RESET}")
                else:
                    logger.error(f"{Fore.RED}Manifest not ready{Fore.RESET}")
                logger.debug("\n"*1)
                    
                logger.debug("listing blink.cameras.items:")
                for name, camera in blink.cameras.items():
                    logger.debug(f"{camera.name} status arm: {blink.cameras[name].arm}")
                logger.debug("\n"*1)
                    
                new_vid = await my_sync.check_new_videos()
                logger.debug(f"New videos?: {new_vid}")

            # download videos
            manifest = my_sync._local_storage["manifest"]
            for item in reversed(manifest):
                dt = item.created_at.astimezone().isoformat().replace(':','-')
                filepath = f"{FOLDER_VIDEOS_BLINK}/../{FOLDER_LOCAL}/{dt[:10]}/{item.name}-{dt}_sync.mp4" # dt[:10]} is date folder
                create_dir_if_not_exists(os.path.dirname(filepath))
                
                if os.path.exists(filepath):
                    logger.info(f"{Fore.YELLOW}\t sync skipping: {filepath}{Fore.RESET}")
                    continue
                else:
                    logger.info(f"{Fore.GREEN}\t sync downloading: {filepath}{Fore.RESET}")
                    logger.info(f"{Fore.CYAN}\t item: {item.name} {item.id} {Fore.RESET}") # {item}
                    
                    await item.prepare_download(blink) # ? copy usb to cloud?
                    await item.download_video(blink, filepath)
                    await asyncio.sleep(DELAY)
        
    # all done return
    return blink


def file_exists_and_not_empty(file_path):
    """Check if a file exists and is not empty."""
    return os.path.isfile(file_path) and os.path.getsize(file_path) > 0

if __name__ == "__main__":
    
    colorama.init()
    
    # ------------------------------------------------
    # | run blink: log in...
    # ------------------------------------------------
    if B_BLINK:
        #logger.info(f"\n{Fore.CYAN}{art.text2art("BLINK", font=ASCIIFONT)}")
        util.logo("blink")
        util.countdown()
        blink = asyncio.run(blink_start())
        
    # Properly close the Blink session TODO ???
    ### await blink.async_util.logout()

    # ------------------------------------------------
    # | sort & copy blink video files to local date folder    
    # ------------------------------------------------
    if B_FOLDERS:
        #logger.info(f"\n{Fore.CYAN}{art.text2art("folders", font=ASCIIFONT)}")
        util.logo("folders")
        util.countdown()
        
        logger.info(f"saving videos to {Fore.MAGENTA}{FOLDER_CLOUD}{Fore.RESET}\n")

        mp4_files = scan_directory_for_mp4(FOLDER_VIDEOS_BLINK)
        logger.info(f"Found {len(mp4_files)} files ending with \"{EXT}\" \n")

        videos_to_delete = []

        for index, file in enumerate(mp4_files):
            logger.debug(file)
            camera_str, date_str, time_str, tz = extract_blink_utc_datetime(file)
            # time_str_extra = time_str[-6:]  # could mean UTC -00-00
            # time_str = time_str[:-6] # strip tz
            logger.debug(', '.join([camera_str, date_str, time_str, tz]))
            
            local_time = convert_utc_to_local(date_str, time_str, 'Europe/Berlin', "+02-00")
            logger.debug(f"local_time: {local_time}")
            local_date_str = str(local_time)[:10]
            logger.debug(f"date_str: {date_str} --> local_date_str: {local_date_str}")

            local_file = camera_str + "-" + str(local_time) + EXT
            # 2-g8t1-gj01-3205-1xhg-2024-09-12T23-48-04+02-00.mp4
            logger.debug(f"{local_file}")
            
            date_dir = os.path.join(FOLDER_VIDEOS_BLINK, f"../{FOLDER_CLOUD}/", local_date_str) # date_str
            create_dir_if_not_exists(date_dir)
        
            src_path  = os.path.join(FOLDER_VIDEOS_BLINK, file)
            dest_path = os.path.join(date_dir, local_file) 
            prefix = f"{index+1}/{len(mp4_files)} -"
            if not os.path.exists(dest_path):
                try:
                    shutil.copy(src_path, dest_path) # move
                    #logger.info(f"{prefix} copied {Fore.GREEN}{src_path} \n\tto \n\t{dest_path}")
                    logger.info(f"{prefix} shutil.copy {Fore.RED}{file} {Fore.LIGHTBLACK_EX}to {Fore.GREEN}{date_dir}")
                    #######videos_to_delete.append(src_path)  
                except Exception as e:
                    logger.error(f"{prefix} Error moving {file}: \n\t{e}") 
            else:
                logger.warning(f"{prefix} skipping {file}...")
                # # # issue: skipped videos remain in the blink folder TODO
                ######videos_to_delete.append(src_path)  
               
                # # trash_dir = os.path.join(FOLDER_VIDEOS_BLINK, f"__trash")
                # # create_dir_if_not_exists(trash_dir)
                # # trash_path = os.path.join(trash_dir, file)
                # # try:
                # #     shutil.move(src_path, trash_path) # move
                # #     logger.info(f"{prefix} moved {Fore.RED}{file} {Fore.LIGHTBLACK_EX}to {Fore.GREEN}{trash_dir}")
                # # except Exception as e:
                # #     logger.error(f"{prefix} Error moving {file} to trash: \n\t{e}") 

            if file_exists_and_not_empty(dest_path):
                logger.debug(f"{prefix} {Fore.GREEN}file exists and is not empty: {dest_path}")
                videos_to_delete.append(src_path)

        ### for mp4_files

    util.countdown()
    blink.auth = None
    blink = None  # Clear the blink instance to release any data.

    # ------------------------------------------------
    # | delete temp files  
    # ------------------------------------------------
    util.logo("delete files")
    secure_delete.secure_random_seed_init()
    util.countdown()
    
    for file in FILES_TO_SECURE_DELETE:        
        if os.path.exists(file):
            try:
                secure_delete.secure_delete(file) ###os.remove(file)
                logger.info(f"securely deleted {file}")
            except Exception as e:
                logger.error(f"Error deleting {file}: {e}")
        else:
            logger.warning(f"File not found: {file}")
    util.logo("done secure_delete.")

    if videos_to_delete:
        logger.warning(f"\nNow delete all videos in BLINK-app.")
        result = messagebox.showwarning("Warning", "Now delete all videos in BLINK-app.")
        
        logger.warning(f"videos_to_delete: {len(videos_to_delete)} files:")
        for file in videos_to_delete:
            logger.info(f"\t{os.path.basename(file)}")
        
        result = messagebox.askokcancel("Confirm", "Now we will delete the complete list videos_to_delete")
        logger.info("User clicked OK" if result else "User clicked Cancel")

        if result: # delete all blink videos
            for file in videos_to_delete:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        #secure_delete.secure_delete(file)
                        logger.info(f"securely deleted {file}")
                    except Exception as e:
                        logger.error(f"Error deleting {file}: {e}")
                else:
                    logger.warning(f"File not found: {file}")

            ###
        ###
        util.logo("done delete files.")
    else:
        logger.info("No videos to delete.")
    ###

    exit(0)

"""
    dev notes
    
    TODO  clean this up
    
    When you attempt to log in to your Blink account you’ll receive a one-time, six-digit code to verify it's you. This is sent to your mobile device as a text message (SMS). You can choose to receive this one-time passcode via the email address you have listed on your Blink account or on your phone as a text message (SMS).

    https://support.blinkforhome.com/en_US/account-and-login/multiple-factor-security

    Tap Settings at the bottom of your home screen.
    Select Account and Privacy > Account Management.
    On the Account and Privacy screen tap Phone Number.
    You will be prompted to enter your Blink account password.
    Note: If you have forgotten your password, you must reset your password before you can update your phone settings. If you no longer have access to the account phone number associated with your Blink account, contact customer support for assistance.
    On the Change Phone Number screen, tap Receive code by and select Voice call.
    Both mobile and landline numbers can be used with the Voice call option. Contact customer support if you have any concerns.


    Check if your mobile device carrier is flagging your code notification as spam.
    If you are receiving your PIN via email, kindly check your email's spam, trash, and promotions folders. If you still cannot find it, try accessing your email on a different mobile device or computer.

    ..................
    
    What should I do if I don't receive an SMS?

    If you don't receive the SMS text to complete your Blink registration, make sure your phone has international SMS text messaging permissions or is connected to the internet to receive the confirmation code via WhatsApp.

    Check the following steps: 

        Check Signal and Coverage: Ensure you have strong signal and network coverage.

        Restart Connection: Try restarting your connection by toggling Airplane mode on and off.

        Login with email instead: If you have already associated an email with your account, you can use it to log in instead of SMS verification.

        Check Phone Number: Double-check if you entered your phone number correctly. If there's a typo, correct it and try again.

        Wait for Retry: Blink allows up to 4 attempts per 3 days for SMS delivery. If you have already exceeded this limit, you will need to wait until the cooldown period expires before trying again.
    

    ...........................................
    ...........................................
    ...........................................


"""