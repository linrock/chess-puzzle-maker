from colorama import Fore, Style

class bcolors:
    HEADER = Style.BRIGHT + Fore.MAGENTA
    BLUE = Style.BRIGHT + Fore.BLUE
    GREEN = Style.BRIGHT + Fore.GREEN
    GRAY = Style.DIM

    WARNING = Style.BRIGHT + Fore.YELLOW
    FAIL = Style.BRIGHT + Fore.RED
    ENDC = Style.RESET_ALL
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
