def convert_obj_type_to_name(self, event_type):
    for action, prop in self.actions_library.items():
        if prop[0] == event_type:
            return action

def seek_player(self, timeout):
    look_around = self.robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    try:
        self.player = self.robot.world.wait_for_observed_face(timeout)
    except asyncio.TimeoutError:
        pass
    finally:  # whether we find it or not, we want to stop the behavior
        look_around.stop()

    if self.player and self.player.is_visible:
        robot.turn_towards_face(self.player).wait_for_completed()
        self.robot.play_anim_trigger(cozmo.anim.Triggers.AcknowledgeFaceNamed).wait_for_completed()
    else:
        print("Player not found")

def __del__(self):
    """Wait for tasks completion before exiting (needed by the Cozmo SDK)"""
    time.sleep(2)

def set_to_seek_position(self):
    """Move lift down, tilt head up"""
    self.robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE / 2).wait_for_completed()
    self.robot.set_lift_height(0, in_parallel=True).wait_for_completed()


def play_with_human():
    mode = None
    while not mode:
        mode = input("Will a player play the game with Cozmo?\n\tyes: [Y]\n\tno: [N]\n")
        if mode == 'Y':
            return True
        elif mode == 'N':
            return False
        print("Sorry I did not understand your choice, please try again.")
