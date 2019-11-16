def setup_game(self):
    """Wait for the player to show the instructions and
    store them till the player shows the EOT marker"""
    self.add_markers_detection()
    while not self.seek(30, self.robot.world.wait_for_observed_face, cozmo.anim.Triggers.AcknowledgeFaceNamed):
        self.robot.play_anim_trigger(cozmo.anim.Triggers.NothingToDoBoredIdle).wait_for_completed()
    while self.instructions[-1] != "EOT":  # Wait for end marker
        time.sleep(0.2)
    print(f"All {len(self.instructions)} instructions have been stored and will now be executed by Cozmo")

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
                                                297, 210, MARKERS_SIZE, True):
            print(f"Marker {action} definition failed!")
