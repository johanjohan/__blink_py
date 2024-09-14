import subprocess
import os
import art
import colorama

FONT="isometric3"

if __name__ == "__main__":
    
    try:
        colorama.init()

        print(art.text2art("start", font=FONT))

        # Path to a Python interpreter that runs any Python script
        # under the virtualenv /path/to/virtualenv/
        python_bin = "D:/__BUP_V_KOMPLETT/X/111_BUP/33projects/__blink_py/venv/Scripts/python.exe"
        script_file = "D:/__BUP_V_KOMPLETT/X/111_BUP/33projects/__blink_py/download_videos.py"

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