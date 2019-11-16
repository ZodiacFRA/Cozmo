import asyncio
import time

import cozmo
from cozmo.objects import CustomObjectMarkers as co_markers
from cozmo.objects import CustomObjectTypes as co_types

from utils import play_with_human
from actions import detect_cube, approach_cube, raise_forklift, lower_forklift, turn_left, turn_right, \
                    move_forward, move_backward


class Robot(object):
    def __init__(self, robot):
        self.r = robot
        self.instructions = []
        self.markers_size = 180  # mm
        self.player = None
        self.actions_library = {
            "detect_cube": [co_types.CustomType00, co_markers.Hexagons2, detect_cube],
            "approach_cube": [co_types.CustomType01, co_markers.Hexagons3, approach_cube],
            "raise_forklift": [co_types.CustomType02, co_markers.Triangles3, raise_forklift],
            "lower_forklift": [co_types.CustomType03, co_markers.Triangles4, lower_forklift],
            "turn_left": [co_types.CustomType04, co_markers.Circles2, turn_left],
            "turn_right": [co_types.CustomType05, co_markers.Circles3, turn_right],
            "move_forward": [co_types.CustomType06, co_markers.Diamonds4, move_forward],
            "move_backward": [co_types.CustomType07, co_markers.Diamonds3, move_backward],
            "EOT": [co_types.CustomType08, co_markers.Triangles2, None]
        }

    def launch(self):
        while True:
            if play_with_human():
                self.setup_game()
                self.execute_instructions()
            else: # Autonomous gameplay
                pass
            time.sleep(1)

    def execute_instructions(self):
        for instruction in self.instructions:
            if self.actions_library[2]:
                self.actions_library[2](self.robot)

    def setup_game(self):
        """Wait for the player to show the instructions and
        store them till the player shows the EOT marker"""
        self.add_markers_detection()
        while not self.seek_player():  # Wait for player detection
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

    def convert_obj_type_to_name(self, event_type):
        for action, prop in self.actions_library.items():
            if prop[0] == event_type:
                return action

    def seek_player(self, timeout):
        """Move lift down, tilt head up, then turn around to find a face"""
        self.robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE / 2).wait_for_completed()
        self.robot.set_lift_height(0, in_parallel=True).wait_for_completed()
        start_time, face = time.time(), None
        while not face and ((time.time() - start_time) < timeout):
                self.robot.turn_in_place(degrees(36))
                try:
                    face = self.robot.world.wait_for_observed_face(2)
                except asyncio.TimeoutError:
                    pass
        if face and face.is_visible:
            robot.turn_towards_face(face).wait_for_completed()
            self.robot.play_anim_trigger(cozmo.anim.Triggers.AcknowledgeFaceNamed).wait_for_completed()
            self.player = face
        else:
            print("No player found")

    def __del__(self):
        """Wait for tasks completion before exiting (needed by the Cozmo SDK)"""
        time.sleep(2)
