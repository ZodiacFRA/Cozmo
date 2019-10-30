import asyncio
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps


class Robot(object):
    def __init__(self, robot):
        self.robot = robot
        self.cube_target = None
        self.face_target = None
        self.cards = []

    def __del__(self):
        time.sleep(2)  # Wait for tasks completion before exiting

    def launch(self):
        # Test only ATM
        self.set_to_seek_position()
        while 42:
            self.seek_player(15)
            if not self.face_target:
                print("Could not find a player")
                self.robot.play_anim_trigger(cozmo.anim.Triggers.NothingToDoBoredIdle).wait_for_completed()
            else:
                self.robot.say_text("Let's play a game!").wait_for_completed()
                break

    def seek_player(self, timeout):
        start_time = time.time()
        while ((time.time() - start_time) < timeout) and not self.face_target:
            tmp = self.robot.turn_in_place(degrees(36))
            self.face_target = self.find_face_in_fov(2)  # Check for faces during 2 secs
            tmp.wait_for_completed()
            if self.face_target and self.face_target.is_visible:
                self.robot.turn_towards_face(self.face_target).wait_for_completed()
                self.robot.play_anim_trigger(cozmo.anim.Triggers.AcknowledgeFaceNamed).wait_for_completed()
                break

    def find_face_in_fov(self, timeout=30):
        face = None
        try:
            face = self.robot.world.wait_for_observed_face(timeout)
        except asyncio.TimeoutError:
            print("Couldn't find a face.")
        return face

    def move_forklit(self, speed=3):
        """Positive speed goes up"""
        self.robot.move_lift(speed)

    def turn(self, angle=90):
        """Positive angle goes left"""
        self.robot.turn_in_place(degrees(angle)).wait_for_completed()

    def move(self, distance=100, speed=150):
        self.robot.drive_straight(distance_mm(distance), speed_mmps(speed)).wait_for_completed()

    def speak(self, msg="I don't know what to say"):
        self.robot.say_text(msg).wait_for_completed()

    def set_to_seek_position(self):
        """Move lift down, tilt head up, turn around to find something"""
        action1 = self.robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE / 2)
        action2 = self.robot.set_lift_height(0, in_parallel=True)
        action1.wait_for_completed()
        action2.wait_for_completed()
