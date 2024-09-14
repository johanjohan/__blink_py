"""
    https://github.com/fronzbot/blinkpy

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
    
    Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Style: DIM, NORMAL, BRIGHT, RESET_ALL
 
"""
import asyncio
from aiohttp import ClientSession
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
import os
import logging
import shutil
from datetime import datetime
import pytz
import json
import blinkpy.helpers.util as util
#from blinkpy.helpers.util import json_load
import art
import colorama 
from colorama import Fore, Back, Style
from sortedcontainers import SortedSet

# ------------------------------------------------
# | params
# ------------------------------------------------

EXT         = ".mp4"
OUTDIR      = os.path.abspath("__blink_videos") # "../__blink_videos"
CAMERA_NAME = "all"
CREDENTIALS = "blink_credentials.json" # "../__blink_credentials.json"

ASCIIFONT   = 'isometric3'

FOLDER_CLOUD= "sorted_cloud"
FOLDER_LOCAL= "sorted_local"

B_BLINK     = True
B_CLOUD     = True
B_SYNC      = True
B_FOLDERS   = True

# ------------------------------------------------
# | init
# ------------------------------------------------
colorama.init()
print(Fore.YELLOW + art.text2art("blink", font=ASCIIFONT) + Fore.RESET)
#print(Fore.CYAN + art.text2art("config", font=ASCIIFONT) + Fore.RESET)

# change cwd
if False:
    print(f"current working dir: {os.getcwd()}")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"current working dir: {os.getcwd()}")
    # input("Press Enter to continue...")
    # exit(0)
# ------------------------------------------------
# |
# ------------------------------------------------
def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            #print(f"Directory created: {dir_path}")
        except Exception as e:
            print(f"Error creating directory {dir_path}: {e}")
    else:
        #print(f"Directory already exists: {dir_path}")
        pass
        
def scan_directory_for_mp4(outdir):
    # Ensure the directory exists
    if not os.path.isdir(outdir):
        print(f"The directory {outdir} does not exist.")
        return []

    # List all files in the directory
    files = os.listdir(outdir)

    # Filter files ending with ".mp4"
    mp4_files = [file for file in files if file.lower().endswith(EXT)]

    return mp4_files

def extract_datetime(filename):
    # 2-g8t1-gj01-3205-1xhg-2024-09-12t18-59-39-00-00.mp4
    # Remove the file extension
    basename = os.path.splitext(filename)[0]

    # Get the last 25 characters of the basename
    date_time_str = basename[-25:]
    camera_str = basename[:-26] # -

    # Extract date and time
    date_str = date_time_str[:10]  # "2024-09-12" # UTC
    time_str = date_time_str[11:]  # "18-59-39-00-00"

    return camera_str, date_str, time_str
    
def convert_utc_to_local(date_str, time_str, local_timezone_str, local_z_str):
    # Combine date and time strings into one string
    date_time_str = f"{date_str}T{time_str}"
    
    # Parse the combined string into a datetime object
    try:
        utc_dt = datetime.strptime(date_time_str, '%Y-%m-%dT%H-%M-%S')
    except ValueError as e:
        print(f"Error parsing datetime: {e}")
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
# | logger
# ------------------------------------------------
#print(Fore.CYAN + art.text2art("logger", font=ASCIIFONT) + Fore.RESET)

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to DEBUG
    #format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define the log message format
    format='%(message)s',  # Define the log message format
    handlers=[
        logging.StreamHandler()  # Output logs to the console
    ]
)

# ------------------------------------------------
# | OUTDIR
# ------------------------------------------------


# ------------------------------------------------
# |
# ------------------------------------------------

# blink
async def start():
    
    blink = Blink()
    auth = Auth(await util.json_load(CREDENTIALS))
    blink.auth = auth
    await blink.start()
    
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
        print(Fore.CYAN + art.text2art("save cloud", font=ASCIIFONT) + Fore.RESET)
        create_dir_if_not_exists(OUTDIR)
        print(f"saving videos to {OUTDIR}\n")
        
        await blink.download_videos(
            path=OUTDIR, 
            camera=CAMERA_NAME,
            since="2024/01/01 00:00", 
            stop=1000, 
            delay=2
        ) 
    

    # NEW TODO - from blinksync.py
    # await blink.save(f"{OUTDIR}/../__temp_blink.json") # OK!!!

    # ------------------------------------------------
    # | sync module
    # ------------------------------------------------
    
    if B_SYNC:
        print(Fore.CYAN + art.text2art("save sync", font=ASCIIFONT) + Fore.RESET)
        print(f"Sync status: {blink.network_ids}")
        print(f"Sync len: {len(blink.networks)}")   
        print(f"Sync: {blink.networks}")   
        assert len(blink.networks) > 0
        
        my_sync: BlinkSyncModule = blink.sync[
            blink.networks[list(blink.networks)[0]]["name"]
        ]        

        # verbose cams
        if False:
            for name, camera in blink.cameras.items():
                print(name)
                print(camera.attributes)
                print()

        # local storage
        my_sync._local_storage["manifest"] = SortedSet()
        await my_sync.refresh()
        
        # verbose _local_storage
        if False:
            if my_sync.local_storage and my_sync.local_storage_manifest_ready:
                print(f"{Fore.GREEN}Manifest is ready{Fore.RESET}")
                print(f"Manifest {Fore.CYAN}{my_sync._local_storage['manifest']}{Fore.RESET}")
            else:
                print(f"{Fore.RED}Manifest not ready{Fore.RESET}")
            print("\n"*1)
                
            for name, camera in blink.cameras.items():
                print(f"{camera.name} status arm: {blink.cameras[name].arm}")
            print("\n"*1)
                
            new_vid = await my_sync.check_new_videos()
            print(f"New videos?: {new_vid}")

        # download videos
        manifest = my_sync._local_storage["manifest"]
        for item in reversed(manifest):
     
            # D:\__BUP_V_KOMPLETT\X\111_BUP\33projects\__blink_py\__blink_videos/__sync__/2-G8T1-GJ01-3205-1XHG_2024-09-11T06_05_17+02_00.mp4   
            dt = item.created_at.astimezone().isoformat().replace(':','-')
            # folder_date = dt[:10]
            # print(f"folder_date: {folder_date}")
            filepath = f"{OUTDIR}/../{FOLDER_LOCAL}/{dt[:10]}/{item.name}-{dt}_sync.mp4"
            create_dir_if_not_exists(os.path.dirname(filepath))
            
            if os.path.exists(filepath):
                print(f"{Fore.YELLOW}\t skipping: {filepath}{Fore.RESET}")
                continue
            else:
                print(f"{Fore.GREEN}\t downloading: {filepath}{Fore.RESET}")
                print(f"{Fore.CYAN}\t item: {item.name} {item.id} {Fore.RESET}") # {item}
                
                await item.prepare_download(blink) # ? copy usb to cloud?
                await item.download_video(blink, filepath)
                await asyncio.sleep(2)
        
    # all done return
    return blink

# ------------------------------------------------
# | run blink
# ------------------------------------------------
if B_BLINK:
    blink = asyncio.run(start())
    
# Properly close the Blink session
### await blink.async_logout()

# ------------------------------------------------
# | move file to local date folder    
# ------------------------------------------------
if B_FOLDERS:
    print(Fore.CYAN + art.text2art("folders", font=ASCIIFONT) + Fore.RESET)

    mp4_files = scan_directory_for_mp4(OUTDIR)
    print(f"Found files ending with {EXT}: {len(mp4_files)}\n")

    for index, file in enumerate(mp4_files):
        #print(file)
        camera_str, date_str, time_str = extract_datetime(file)
        time_str_extra = time_str[-6:]  # could mean UTC -00-00
        time_str = time_str[:-6] # strip tz
        #print(camera_str, date_str, time_str, time_str_extra)
        
        local_time = convert_utc_to_local(date_str, time_str, 'Europe/Berlin', "+02-00")
        #print(f"local_time: {local_time}")
        local_date_str = str(local_time)[:10]
        #print(f"date_str: {date_str} --> local_date_str: {local_date_str}")

        local_file = camera_str + "-" + str(local_time) + EXT
        # 2-g8t1-gj01-3205-1xhg-2024-09-12T23-48-04+02-00.mp4
        #print(f"{local_file}")
        
        date_dir = os.path.join(OUTDIR, f"../{FOLDER_CLOUD}/", local_date_str) # date_str
        create_dir_if_not_exists(date_dir)
     
        src_path  = os.path.join(OUTDIR, file)
        dest_path = os.path.join(date_dir, local_file) 
        print(f"{index+1}/{len(mp4_files)} - ", end='')
        if not os.path.exists(dest_path):
            try:
                ###shutil.move(src_path, dest_path)
                shutil.copy(src_path, dest_path)
                print(f"copied \n\t{Fore.GREEN}{src_path} \n\tto \n\t{dest_path}")
            except Exception as e:
                print(f"Error moving \n\t{Fore.RED}{file}: \n\t{e}") 
        else:
            print(f"skipping \n\t{Fore.YELLOW}{dest_path}...")

        #print(f"{Fore.RESET}\n"*1)            
        print(f"{Fore.RESET}", end='')        