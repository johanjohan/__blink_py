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
        python_bin  = f"{my_dir}/venv/Scripts/python.exe"
        script_file = f"{my_dir}/download_videos.py"
        
        logo(Path(script_file).stem)

        # set cwd to script_file for folder paths relative to this file
        #print(f"current working dir: {os.getcwd()}")
        os.chdir(os.path.dirname(os.path.abspath(script_file)))
        print(f"changed working dir: {os.getcwd()} \n\n")

        print(Fore.LIGHTBLACK_EX + ' '.join([python_bin, script_file]) + Fore.RESET)
        p1 = subprocess.Popen([python_bin, script_file])
        p1.wait()
        
    except Exception as e:
        print(e)
    
    logo("all done.")
    input("press enter to continue...")
    exit(0)