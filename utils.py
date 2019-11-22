C_RED = "\x1b[31m"
C_GREEN = "\x1b[32m"
C_YELLOW = "\x1b[33m"
C_BLUE = "\x1b[36m"
C_RESET = "\x1b[0m"

MARKERS_SIZE = 40

HUMAN = 1
ROBOT = 0


def play_with_human():
    mode = None
    while not mode:
        mode = input(f"{C_BLUE}Will a player play the game with Cozmo?\n ->yes: [Y]\n ->no: [N]\n{C_RESET}")
        if mode == 'Y':
            return True
        elif mode == 'N':
            return False
        print(f"{C_RED}Sorry I did not understand your choice, please try again.{C_RESET}")


def color_print(msg, color):
    print(color + msg, C_RESET)
