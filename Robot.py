import asyncio
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps


class Robot(object):
    def __init__(self, robot):
        self.robot = robot
        self.cube_target = None
        self.face_target = None
        self.current_behavior = None
        self.cards = []

    def __del__(self):
        time.sleep(2)  # Wait for tasks completion before exiting

    def launch(self):
		# Test only ATM
        self.move_forklit(-1)
        self.turn()
        self.turn()
        self.speak("I'm gonna move")
        self.move()
        self.speak("I'm done!")

    def move_forklit(self, speed=3):
        """Positive speed goes up"""
        self.robot.move_lift(speed)

    def turn(self, angle=90):
        """Positive angle goes left"""
        self.robot.turn_in_place(degrees(angle)).wait_for_completed()

    def move(self, distance=100, speed=50):
        self.robot.drive_straight(distance_mm(distance), speed_mmps(speed)).wait_for_completed()

    def speak(self, msg="I don't know what to say"):
        self.robot.say_text(msg).wait_for_completed()
