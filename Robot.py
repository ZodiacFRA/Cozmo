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
        self.set_to_seek_position()
        self.seek_faces(15)

    def seek_faces(self, timeout):
        start_time = time.time()
        face = None
        while ((time.time() - start_time) < timeout) and not face:
                self.robot.turn_in_place(degrees(36))
                face = self.find_face_in_fov(2)
        if face and face.is_visible:
            self.robot.set_all_backpack_lights(cozmo.lights.blue_light)
        else:
            self.robot.set_backpack_lights_off()

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
        action1 = self.robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE)
        action2 = self.robot.set_lift_height(0, in_parallel=True)
        action1.wait_for_completed()
        action2.wait_for_completed()
