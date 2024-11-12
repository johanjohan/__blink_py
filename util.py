from colorama import Fore, Back, Style
import art
from tqdm import tqdm
import time

# https://github.com/sepandhaghighi/art/blob/master/FontList.ipynb
# FONT = "tarty2" # isometric3 4max bubble digital drpepper future_8 +tarty2 +thin3 tiny2 

def logo(_msg, _font="tarty2", _fore=Fore.YELLOW):
    print(f"\n{_fore}{art.text2art(_msg.upper(), font=_font)}{Fore.RESET}\n")
 
# https://github.com/sepandhaghighi/art/blob/master/FontList.ipynb 
def countdown(_secs=3, _msg="", _fore=Fore.LIGHTBLACK_EX, _font="ticks"): # LIGHTBLACK_EX funky_dr block2  ticks univers varsity black_bubble  fancy141 tarty3 
    if False:
        for i in range(int(_secs)):
            s = str(_secs-i)
            if True:
                print(f"{_fore}{s}{Fore.RESET}   ", end='')
            else:
                s = art.text2art(str(_secs-i) + _msg, font=_font)
                logger.info(f"{_fore}{s}{Fore.RESET}")
            time.sleep(1)
        print()
    else:
        # bar_format = '|{bar:40}| '
        # bar_format = '{l_bar}{bar:60}{r_bar}{bar:-10b}'
        # bar_format = '{l_bar}{bar:60} {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        bar_format = '{bar:44} {remaining}\t'
        #bar_format = "{desc}: {percentage:.1f}%|{bar:80}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        tqdm.write(f"{_fore}", end='\n')
        div = 1.0
        for i in tqdm(range(int(_secs * div)), bar_format=bar_format): #  ncols=80 bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
            time.sleep(1.0/div)
        tqdm.write(f"{Fore.RESET}", end='\n')
    
      
"""
    Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Style: DIM, NORMAL, BRIGHT, RESET_ALL
    
    
    print()
    print(Fore.BLACK + 'BLACK')
    print(Fore.BLUE + 'BLUE')
    print(Fore.CYAN + 'CYAN')
    print(Fore.GREEN + 'GREEN')
    print(Fore.LIGHTBLACK_EX + 'LIGHTBLACK_EX')
    print(Fore.LIGHTBLUE_EX + 'LIGHTBLUE_EX')
    print(Fore.LIGHTCYAN_EX + 'LIGHTCYAN_EX')
    print(Fore.LIGHTGREEN_EX + 'LIGHTGREEN_EX')
    print(Fore.LIGHTMAGENTA_EX + 'LIGHTMAGENTA_EX')
    print(Fore.LIGHTRED_EX + 'LIGHTRED_EX')
    print(Fore.LIGHTWHITE_EX + 'LIGHTWHITE_EX')
    print(Fore.LIGHTYELLOW_EX + 'LIGHTYELLOW_EX')
    print(Fore.MAGENTA + 'MAGENTA')
    print(Fore.RED + 'RED')
    print(Fore.RESET + 'RESET')
    print(Fore.WHITE + 'WHITE')
    print(Fore.YELLOW + 'YELLOW')
    logger.info(f"\n{Fore.YELLOW}{art.text2art("BLINK", font=ASCIIFONT)}") # {Fore.RESET}

"""   
