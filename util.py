from colorama import Fore, Back, Style
import art

def logo(_msg, _font="tarty2", _fore=Fore.YELLOW):
    print(f"\n{_fore}{art.text2art(_msg.upper(), font=_font)}{Fore.RESET}\n")
    
    