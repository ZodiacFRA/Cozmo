def detect_cube(self):
    print("Cube detection not implemented yet!")

def approach_cube(self):
    print("Cube approach implemented yet!")

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
