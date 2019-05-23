from colorama import Fore, Style


class Color(object):
    """ Foreground colors """

    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    MAGENTA = '\033[95m'
    RED = '\033[91m'
    YELLOW = '\033[93m'

    VIOLET = Fore.MAGENTA
    DARK_GREEN = Fore.GREEN
    DARK_BLUE = Fore.BLUE

    BLACK = Style.DIM + Fore.LIGHTBLACK_EX
    DARK_GREY = Style.DIM + Fore.WHITE
    WHITE = Style.NORMAL + Fore.LIGHTWHITE_EX

    DIM = Style.DIM
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
