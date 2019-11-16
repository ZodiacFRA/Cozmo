def detect_cube(robot):
    print("Cube detection not implemented yet!")

def approach_cube(robot):
    print("Cube approach implemented yet!")

def raise_forklift(robot):
    robot.move_lift(3).wait_for_completed()

def lower_forklift(robot):
    robot.move_lift(-3).wait_for_completed()

def turn_left(robot):
    robot.turn_in_place(degrees(90)).wait_for_completed()

def turn_right(robot):
    robot.turn_in_place(degrees(-90)).wait_for_completed()

def move_forward(robot):
    robot.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()

def move_backward(robot):
    robot.drive_straight(distance_mm(-100), speed_mmps(100)).wait_for_completed()

def speak(robot, msg="I don't know what to say"):
    robot.say_text(msg).wait_for_completed()
