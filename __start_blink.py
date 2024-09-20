import subprocess
import os
import art
import colorama
from colorama import Fore, Back, Style
from pathlib import Path
import util

logo = lambda _msg :  util.logo(_msg, _fore=Fore.MAGENTA)

if __name__ == "__main__":
    
    try:
        colorama.init()

        # under the virtualenv /path/to/virtualenv/
        my_dir = os.path.dirname(os.path.abspath(__file__))
        python_bin_local  = f"venv/Scripts/python.exe"
        script_file_local = f"download_videos.py"
        python_bin  = f"{my_dir}/{python_bin_local}"
        script_file = f"{my_dir}/{script_file_local}"
        
        logo(Path(script_file).stem)

        # set cwd to script_file for folder paths relative to this file
        #print(f"current working dir: {os.getcwd()}")
        os.chdir(os.path.dirname(os.path.abspath(script_file)))
        print(f"changed working dir: {os.getcwd()} \n\n")

        print(Fore.LIGHTBLACK_EX + ' '.join([python_bin_local, script_file_local]) + Fore.RESET)
        p1 = subprocess.Popen([python_bin, script_file])
        p1.wait()
        
    except Exception as e:
        print(e)
    
    logo("all done.")
    input("press enter to continue...")
    exit(0)