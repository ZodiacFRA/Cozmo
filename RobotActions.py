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

def detect_cube(self):
    look_around = self.robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    try:
        self.cube = robot.world.wait_for_observed_light_cube(timeout=30)
    except asyncio.TimeoutError:
        print("Cube not found")
    finally:  # whether we find it or not, we want to stop the behavior
        look_around.stop()

def approach_cube(self):
    if not self.cube:
        print("Cozmo does not remeber any cube!")
    else:
        self.robot.go_to_object(self.cube, distance_mm(70.0)).wait_for_completed()

def raise_forklift(self):
    self.robot.move_lift(3).wait_for_completed()

def lower_forklift(self):
    self.robot.move_lift(-3).wait_for_completed()

def turn_left(self):
    self.robot.turn_in_place(degrees(90)).wait_for_completed()

def turn_right(self):
    self.robot.turn_in_place(degrees(-90)).wait_for_completed()

def move_forward(self):
    self.robot.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()

def move_backward(self):
    self.robot.drive_straight(distance_mm(-100), speed_mmps(100)).wait_for_completed()

def speak(self, msg="I don't know what to say"):
    self.robot.say_text(msg).wait_for_completed()
