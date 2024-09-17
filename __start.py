import subprocess
import os
import art
import colorama
from colorama import Fore, Back, Style
from pathlib import Path
import util

# https://github.com/sepandhaghighi/art/blob/master/FontList.ipynb
FONT = "tarty2" # isometric3 4max bubble digital drpepper future_8 +tarty2 +thin3 tiny2 

logo = lambda _msg :  util.logo(_msg, _fore=Fore.MAGENTA)

# def logo(_msg):
#     #print(f"\n\n{Fore.MAGENTA}3j - {art.text2art(_msg.upper(), font=FONT)}{Fore.RESET}\n")
#     util.logo(_msg, _fore=Fore.MAGENTA)

if __name__ == "__main__":
    
    try:
        colorama.init()

        # Path to a Python interpreter that runs any Python script
        # under the virtualenv /path/to/virtualenv/
        my_dir = os.path.dirname(os.path.abspath(__file__))
        python_bin  = f"{my_dir}/venv/Scripts/python.exe"
        script_file = f"{my_dir}/download_videos.py"
        
        logo(Path(script_file).stem)
        #exit(0)

        # set cwd to script_file
        print(f"current working dir: {os.getcwd()}")
        os.chdir(os.path.dirname(os.path.abspath(script_file)))
        print(f"changed working dir: {os.getcwd()} \n\n")

        print([python_bin, script_file])
        p1 = subprocess.Popen([python_bin, script_file])
        p1.wait()
        
    except Exception as e:
        print(e)
        
        
    logo("all done.")
    input("press enter to continue...")
    exit(0)