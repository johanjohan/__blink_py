"""
uv init --python 3.12
pip install pygame==2.6.0
pygame==2.6.0; sys_platform != "win32"
uv run __start_blink.py
"""

import subprocess
import os
import art
import colorama
from colorama import Fore, Back, Style
from pathlib import Path
import util

# --------------------------------------------------------
# | this script starts download_videos.py using the      |
# | virtualenv python interpreter                        |
# --------------------------------------------------------

logo = lambda _msg :  util.logo(_msg, _fore=Fore.MAGENTA)

if __name__ == "__main__":
    
    try:
        colorama.init()

        # under the virtualenv /path/to/virtualenv/
        my_dir = os.path.dirname(os.path.abspath(__file__))
        python_bin_local  = ".venv/Scripts/python.exe"
        assert os.path.exists(f"{my_dir}/{python_bin_local}"), f"python binary not found: {my_dir}/{python_bin_local}"
        script_file_local = "download_videos.py"
        
        python_bin  = f"{my_dir}/{python_bin_local}"
        script_file = f"{my_dir}/{script_file_local}"
        
        logo(Path(script_file).stem)

        # set cwd to script_file for folder paths relative to this file
        os.chdir(os.path.dirname(os.path.abspath(script_file)))
        print(f"changed working dir: {os.getcwd()} \n\n")

        print("\t", Fore.LIGHTBLACK_EX + ' '.join([python_bin_local, script_file_local]) + Fore.RESET)
        p1 = subprocess.Popen([python_bin, script_file])
        p1.wait()
        
    except Exception as e:
        print(e)
    
    logo("all done.")
    input("press enter to continue...")
    exit(0)