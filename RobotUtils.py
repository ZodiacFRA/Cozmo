def convert_obj_type_to_name(self, event_type):
    for action, prop in self.actions_library.items():
        if prop[0] == event_type:
            return action

def __del__(self):
    """Wait for tasks completion before exiting (needed by the Cozmo SDK)"""
    time.sleep(2)

def set_to_seek_position(self):
    """Move lift down, tilt head up"""
    self.robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE / 2).wait_for_completed()
    self.robot.set_lift_height(0, in_parallel=True).wait_for_completed()

def handle_object_appeared(self, evt, **kw):
    if isinstance(evt.obj, cozmo.objects.CustomObject):
        action_name = self.convert_obj_type_to_name(evt.obj.object_type)
        print(f"{action_name} appears")
        if self.instructions[-1] != action_name:
            self.instructions.append(action_name)

def handle_object_disappeared(self, evt, **kw):
    if isinstance(evt.obj, cozmo.objects.CustomObject):
        print(f"{str(evt.obj.object_type)} disappear")

def add_markers_detection(self):
    self.r.add_event_handler(cozmo.objects.EvtObjectAppeared, self.handle_object_appeared)
    self.r.add_event_handler(cozmo.objects.EvtObjectDisappeared, self.handle_object_disappeared)
    for action, marker_prop in ACTIONS.items():
        if not self.r.world.define_custom_wall(marker_prop[0], marker_prop[1],
                                                297, 210, self.markers_size, True):
            print(f"Marker {action} definition failed!")


def play_with_human():
    mode = None
    while not mode:
        mode = input("Will a player play the game with Cozmo?\n\tyes: [Y]\n\tno: [N]\n")
        if mode == 'Y':
            return True
        elif mode == 'N':
            return False
        print("Sorry I did not understand your choice, please try again.")
