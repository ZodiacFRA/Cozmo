def play_with_human():
    mode = None
    while not mode:
        mode = input("Will a player play the game with Cozmo?\n\tyes: [Y]\n\tno: [N]\n")
        if mode == 'Y':
            return True
        elif mode == 'N':
            return False
        print("Sorry I did not understand your choice, please try again.")
