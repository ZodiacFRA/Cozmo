import asyncio
import time
import random

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
from cozmo.objects import CustomObjectMarkers as co_markers
from cozmo.objects import CustomObjectTypes as co_types
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id

from utils import *


class Robot(object):
    def __init__(self, robot):
        self.r = robot
        self.last_instruction_add_time = time.time()
        self.instructions = []
        self.markers_size = 40  # mm
        self.player = None
        self.cube = None
        self.behavior = None
        self.game_nbr = 0
        self.restart_game_flag = False
        self.start_pos = self.r.pose
        self.actions_library = {
            "detect_cube": [co_types.CustomType00, co_markers.Hexagons2, self.detect_cube],
            "approach_cube": [co_types.CustomType01, co_markers.Hexagons3, self.approach_cube],
            "raise_forklift": [co_types.CustomType02, co_markers.Triangles3, self.raise_forklift],
            "lower_forklift": [co_types.CustomType03, co_markers.Triangles4, self.lower_forklift],
            "turn_left": [co_types.CustomType04, co_markers.Circles2, self.turn_left],
            "turn_right": [co_types.CustomType05, co_markers.Circles3, self.turn_right],
            "move_forward": [co_types.CustomType06, co_markers.Diamonds4, self.move_forward],
            "move_backward": [co_types.CustomType07, co_markers.Diamonds3, self.move_backward],
            "remove_last_instruction": [co_types.CustomType08, co_markers.Hexagons5, None],
            "restart_game": [co_types.CustomType09, co_markers.Triangles5, None],
            "EOT": [co_types.CustomType10, co_markers.Triangles2, None]
        }
        self.acks = [
                "Yes!",
                "Aye aye captain!"
        ]
        # Game sucess: BuildPyramidSuccess, BuildPyramidThankUser
        # Game fail: FistBumpLeftHanging

    def launch(self):
        play_with_human_flag = play_with_human()
        while 42:
            self.restart_game_flag = False
            if not self.game_nbr:
                self.add_markers_detection()
            if play_with_human_flag:
                self.setup_game()
                self.execute_instructions()
            else: # Autonomous gameplay
                self.stack_cubes()
            self.r.go_to_pose(self.start_pos).wait_for_completed()
            self.game_nbr += 1
            tmp_time = time.time()
            self.set_to_seek_face_position()
            self.speak("Do you want to play again?")
            while not "restart_game" in self.instructions and time.time() - tmp_time < 15:
                pass
            if not "restart_game" in self.instructions:
                self.r.play_anim_trigger(cozmo.anim.Triggers.FistBumpLeftHanging).wait_for_completed()
                return
            else:
                print("detected")
                self.r.play_anim_trigger(cozmo.anim.Triggers.MeetCozmoFirstEnrollmentCelebration).wait_for_completed()


    def stack_cubes(self):
        lookaround = self.r.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        cubes = self.r.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)
        lookaround.stop()

        if len(cubes) < 2:
            print("Error: need 2 Cubes but only found", len(cubes), "Cube(s)")
        else:
            # Try and pickup the 1st cube
            current_action = self.r.pickup_object(cubes[0], num_retries=3)
            current_action.wait_for_completed()
            if current_action.has_failed:
                code, reason = current_action.failure_reason
                result = current_action.result
                print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
                return

            # Now try to place that cube on the 2nd one
            current_action = self.r.place_on_object(cubes[1], num_retries=3)
            current_action.wait_for_completed()
            if current_action.has_failed:
                code, reason = current_action.failure_reason
                result = current_action.result
                print("Place On Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
                return

    def setup_game(self):
        """Wait for the player to show the instructions and
        store them till the player shows the EOT marker"""
        # Find a player
        self.set_to_seek_face_position()
        while not self.seek_player(30):
            self.r.play_anim_trigger(cozmo.anim.Triggers.NothingToDoBoredIdle).wait_for_completed()
            time.sleep(1)
        print(f"{C_GREEN}Player found, waiting for instructions{C_RESET}")
        # Get all instructions until EOT marker
        self.instructions.clear()
        while not len(self.instructions) or self.instructions[-1] != "EOT":
            time.sleep(0.2)
        self.instructions.pop()
        print(f"{C_GREEN}All {len(self.instructions)} instructions have been stored and will now be executed by Cozmo{C_RESET}")

    def execute_instructions(self):
        for instruction in self.instructions:
            print(f"{C_BLUE}Executing {instruction}{C_RESET}")
            self.actions_library[instruction][2]()

    def seek_player(self, timeout):
        if self.behavior:
            print(f"{C_RED}Overriding existing behavior!{C_RESET}")
            self.behavior.stop()
        self.behavior = self.r.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)
        try:
            self.player = self.r.world.wait_for_observed_face(timeout)
        except asyncio.TimeoutError:
            pass
        finally:  # whether we find it or not, we want to stop the behavior
            self.behavior.stop()
            self.behavior = None

        if self.player and self.player.is_visible:
            self.r.turn_towards_face(self.player).wait_for_completed()
            self.r.play_anim_trigger(cozmo.anim.Triggers.AcknowledgeFaceNamed).wait_for_completed()
            return True
        else:
            print(f"{C_RED}Player not found{C_RESET}")

    def detect_cube(self):
        if self.behavior:
            print(f"{C_RED}Overriding existing behavior!{C_RESET}")
            self.behavior.stop()
        self.behavior = self.r.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try:
            self.cube = self.r.world.wait_for_observed_light_cube(timeout=30)
        except asyncio.TimeoutError:
            print(f"{C_RED}Cube not found{C_RESET}")
        finally:  # whether we find it or not, we want to stop the behavior
            self.behavior.stop()
            self.behavior = None

    def approach_cube(self):
        if not self.cube:
            print(f"{C_RED}Cozmo does not remeber any cube!{C_RESET}")
        else:
            self.r.go_to_object(self.cube, distance_mm(40.0)).wait_for_completed()

    def raise_forklift(self):
        self.r.move_lift(3)

    def lower_forklift(self):
        self.r.move_lift(-3)

    def turn_left(self):
        self.r.turn_in_place(degrees(90)).wait_for_completed()

    def turn_right(self):
        self.r.turn_in_place(degrees(-90)).wait_for_completed()

    def move_forward(self):
        self.r.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()

    def move_backward(self):
        self.r.drive_straight(distance_mm(-100), speed_mmps(100)).wait_for_completed()

    def speak(self, msg="I'm COZMO'"):
        self.r.say_text(msg).wait_for_completed()

    def convert_obj_type_to_name(self, event_type):
        for action, prop in self.actions_library.items():
            if prop[0] == event_type:
                return action

    def set_to_seek_face_position(self):
        """Move lift down, tilt head up"""
        self.r.set_lift_height(0, in_parallel=True).wait_for_completed()
        self.r.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

    def set_to_seek_cube_position(self):
        """Move lift down, tilt head up"""
        self.r.set_lift_height(0, in_parallel=True).wait_for_completed()
        self.r.set_head_angle(degrees(0)).wait_for_completed()

    def blink(self, blinks):
        blink_speed = 0.05
        for i in range(blinks):
            if i:
                time.sleep(blink_speed)
            self.r.set_all_backpack_lights(cozmo.lights.green_light)
            time.sleep(blink_speed)
            self.r.set_all_backpack_lights(cozmo.lights.blue_light)
            time.sleep(blink_speed)
            self.r.set_all_backpack_lights(cozmo.lights.off_light)

    def handle_object_appeared(self, evt, **kw):
        if isinstance(evt.obj, cozmo.objects.CustomObject):
            action_name = self.convert_obj_type_to_name(evt.obj.object_type)
            print(f"{C_BLUE}{action_name} appears{C_RESET}")
            if time.time() - self.last_instruction_add_time > 3:
                print(f"{C_GREEN} + {action_name.replace('_', ' ').title()}{C_RESET}")
                if action_name == "remove_last_instruction" and len(self.instructions):
                    removed = self.instructions.pop()
                    print(f"{C_RED} - {removed.replace('_', ' ').title()}{C_RESET}")
                else:
                    self.instructions.append(action_name)
                print(f"\r{self.instructions}{C_RESET}", end='')
                self.blink(1)
                self.last_instruction_add_time = time.time()

    def handle_object_disappeared(self, evt, **kw):
        return
        # if isinstance(evt.obj, cozmo.objects.CustomObject):
            # print(f"{C_BLUE}{self.convert_obj_type_to_name(evt.obj.object_type)} disappear{C_RESET}")

    def add_markers_detection(self):
        self.r.add_event_handler(cozmo.objects.EvtObjectAppeared, self.handle_object_appeared)
        self.r.add_event_handler(cozmo.objects.EvtObjectDisappeared, self.handle_object_disappeared)
        for action, marker_prop in self.actions_library.items():
            if not self.r.world.define_custom_cube(marker_prop[0], marker_prop[1],
                                                    50, self.markers_size, self.markers_size, True):
                print(f"{C_RED}Marker {action} definition failed!{C_RESET}")

    def __del__(self):
        """Wait for tasks completion before exiting (needed by the Cozmo SDK)"""
        if self.behavior:
            self.behavior.stop()
        time.sleep(2)
