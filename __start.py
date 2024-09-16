import subprocess
import os
import art
import colorama
from pathlib import Path

# https://github.com/sepandhaghighi/art/blob/master/FontList.ipynb
FONT="4max" # isometric3 4max 

if __name__ == "__main__":
    
    try:
        colorama.init()

        # Path to a Python interpreter that runs any Python script
        # under the virtualenv /path/to/virtualenv/
        my_dir = os.path.dirname(os.path.abspath(__file__))
        python_bin  = f"{my_dir}/venv/Scripts/python.exe"
        script_file = f"{my_dir}/download_videos.py"
        
        #print("\n" + art.text2art(os.path.basename(script_file), font=FONT))
        print("\n" + art.text2art(Path(script_file).stem, font=FONT))

        # set cwd to script_file
        print(f"current working dir: {os.getcwd()}")
        os.chdir(os.path.dirname(os.path.abspath(script_file)))
        print(f"changed working dir: {os.getcwd()} \n\n")

        print([python_bin, script_file])
        p1 = subprocess.Popen([python_bin, script_file])
        p1.wait()
        
    except Exception as e:
        print(e)
        
        
    print(art.text2art("ALL DONE", font=FONT))
    input("press enter to continue...")
    exit(0)