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
    def __init__(s, robot, player_name):
        s.r = robot
        s.pickup_flag = False
        s.actions_library = {
            "pickup_cube": [None, None, s.pickup_cube],
            "place_on_object": [None, None, s.place_on_object],

            "detect_cube": [co_types.CustomType00, co_markers.Hexagons2, s.detect_cube],
            "approach_cube": [co_types.CustomType01, co_markers.Hexagons3, s.approach_cube],
            "raise_forklift": [co_types.CustomType02, co_markers.Triangles3, s.raise_forklift],
            "lower_forklift": [co_types.CustomType03, co_markers.Triangles4, s.lower_forklift],
            "turn_left": [co_types.CustomType04, co_markers.Circles2, s.turn_left],
            "turn_right": [co_types.CustomType05, co_markers.Circles3, s.turn_right],
            "move_forward": [co_types.CustomType06, co_markers.Diamonds4, s.move_forward],
            "move_backward": [co_types.CustomType07, co_markers.Diamonds3, s.move_backward],

            "remove_last_instruction": [co_types.CustomType08, co_markers.Hexagons5, None],
            "EOT": [co_types.CustomType11, co_markers.Triangles2, None],

            "do_interactive_game": [co_types.CustomType09, co_markers.Hexagons4, None],  # Needs marker
            "do_autonomous_game": [co_types.CustomType10, co_markers.Triangles5, None]
        }
        # Game data
        s.game_type = None
        s.instructions = []
        s.player = None
        s.cubes = None
        s.game_log = {"Player name": player_name, "Positions": []}

    def launch(s):
        while 42:
            s.instructions.clear()
            s.record_pos("Game Start")
            s.seek_player()  # Will loop until a player is found
            # Game type handling
            tmp_time = time.time()
            s.speak("Do you want to play with me? Or do I do it on my own?")
            while time.time() - tmp_time < 30:
                if "do_autonomous_game" in s.instructions:
                    s.anim_lost()
                    s.game_log["Game Type"] = "Autonomous"
                    s.game_type = ROBOT
                    s.speak("Ok, I will do it on my own")
                    break
                elif "do_interactive_game" in s.instructions:
                    s.anim_won()
                    s.game_log["Game Type"] = "Interactive"
                    s.game_type = HUMAN
                    break
            else:  # No instructions, quit
                s.speak("Good bye!")
                return

            s.instructions.clear()

            flag = False
            if s.game_type == HUMAN:
                s.get_instructions()
                flag = s.execute_instructions()
            else: # Autonomous gameplay
                flag = s.stack_cubes()

            if flag:
                s.anim_won()
                s.r.go_to_pose(s.game_log["Positions"][1][2]).wait_for_completed()  # Go to Player
                s.r.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
                s.speak("I did it!")
            else:
                s.anim_lost()
                s.r.go_to_pose(s.game_log["Positions"][1][2]).wait_for_completed()  # Go to Player
                s.r.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
                s.speak("I failed!")

            # Log all game data and reset it
            s.player = None

    ######################################
    # Complex Actions
    def approach_cube(s):
        """For player game, in this case"""
        if not s.cubes:
            color_print("Cozmo does not remember any cube!", C_RED)
        else:
            s.r.go_to_object(s.cubes[0], distance_mm(50.0)).wait_for_completed()

    def detect_cube(s, wanted_cube_nbr=1):
        lookaround = s.r.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        # time.sleep(5)
        s.cubes = s.r.world.wait_until_observe_num_objects(num=wanted_cube_nbr, object_type=cozmo.objects.LightCube, timeout=60)
        lookaround.stop()
        if len(s.cubes) < wanted_cube_nbr:
            return color_print(f"Error: need {wanted_cube_nbr} Cubes but only found: {len(s.cubes)} Cube(s)", C_RED)
        return True

    def pickup_cube(s, cube_obj=None, num_retries=3):
        print("pickup cube", s.cubes)
        if not cube_obj:
            cube_obj = s.cubes[0]
        action = s.r.pickup_object(cube_obj, num_retries=num_retries)
        action.wait_for_completed()
        return action

    def place_on_object(s, cube_obj=None, num_retries=3):
        print("pickup cube", s.cubes)
        if not cube_obj:
            cube_obj = s.cubes[0]
        action = s.r.place_on_object(cube_obj, num_retries=num_retries)
        action.wait_for_completed()
        return action

    def stack_cubes(s):
        """For autonomous game"""
        if s.detect_cube(2):
            # Try and pickup the 1st cube
            action = s.pickup_cube(s.cubes[0], num_retries=3)
            if action.has_failed:
                code, reason = action.failure_reason
                if action.result == cozmo.action.ActionResults.BAD_OBJECT:
                    s.stack_cubes()
                if action.result == cozmo.action.ActionResults.CANCELLED_WHILE_RUNNING:
                    s.speak("I can't see enough cubes")
                return color_print(f"Pickup Cube failed! code: {code}\nreason: {reason}\nresult: {action.result}", C_RED)

            # Now try to place that cube on the 2nd one
            action = s.place_on_object(s.cubes[1], num_retries=3)
            if action.has_failed:
                code, reason = action.failure_reason
                return color_print(f"Place on Cube failed! code: {code}\nreason: {reason}\nresult: {action.result}", C_RED)
        return True

    def seek_player(s):
        while 42:
            lookaround = s.r.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)
            color_print("Looking for a player", C_YELLOW)
            try:
                s.player = s.r.world.wait_for_observed_face(timeout=30)
            except:  # Yeah not cool, but.. Cozmo SDK? Can't handle timeouts in there.
                pass
            lookaround.stop()

            if s.player and s.player.is_visible:
                color_print("Player found", C_GREEN)
                s.r.turn_towards_face(s.player).wait_for_completed()
                s.r.play_anim_trigger(cozmo.anim.Triggers.AcknowledgeFaceNamed).wait_for_completed()
                s.record_pos("Player found")
                return
            else:
                color_print("Player not found after 30 seconds, retrying...", C_RED)
            s.r.play_anim_trigger(cozmo.anim.Triggers.NothingToDoBoredIdle).wait_for_completed()

    ######################################
    # Utils
    def record_pos(s, event):
        """Logs the time, event (string) and pose of the robot when called"""
        s.game_log["Positions"].append((time.time(), event, s.r.pose))

    def get_instructions(s):
        """Wait for the player to show the instructions and
        store them, returns when the player shows the EOT marker"""
        s.speak("You can give me the instructions now!")
        while not len(s.instructions) or s.instructions[-1] != "EOT":
            s.speak(' ')
        s.speak("Let's go!")
        color_print(f"All {len(s.instructions)} instructions have been stored and will now be executed by Cozmo", C_GREEN)
        s.instructions.pop()
        for i in range(len(s.instructions) - 1):
            if s.instructions[i] == "approach_cube" and s.instructions[i + 1] == "raise_forklift":  # Check forklift?
                s.pickup_flag = True
                s.instructions.pop(i)
                s.instructions.pop(i)
                s.instructions.insert(i, "pickup_cube")
        if s.pickup_flag:
            for i in range(len(s.instructions) - 1):
                if s.instructions[i] == "approach_cube" and s.instructions[i + 1] == "lower_forklift":  # Check forklift?
                    s.instructions.pop(i)
                    s.instructions.pop(i)
                    s.instructions.insert(i, "place_on_object")
        s.game_log["Instructions"] = s.instructions

    def execute_instructions(s):
        """Execute all stored instructions (from detected markers)"""
        for instruction in s.instructions:
            if s.actions_library[instruction][2]:
                color_print(f"Executing {instruction}", C_BLUE)
                flag = s.actions_library[instruction][2]()
                s.record_pos(instruction)
                if flag == 2:
                    print("return 2")
                    return 2

    def handle_object_appeared(s, evt, **kw):
        """callback for marker detected"""
        if isinstance(evt.obj, cozmo.objects.CustomObject):
            action_name = s.convert_obj_type_to_name(evt.obj.object_type)
            # color_print(f" + {action_name.replace('_', ' ').title()}", C_GREEN)
            if action_name == "remove_last_instruction" and len(s.instructions):
                removed = s.instructions.pop()
                color_print(f" - {removed.replace('_', ' ').title()}", C_RED)
            else:
                s.instructions.append(action_name)
            color_print(f"{s.instructions}", C_BLUE)
            s.blink(2)

    def handle_object_disappeared(s, evt, **kw):
        return

    def add_markers_detection(s):
        """Setup the callback function for marker detection, also defines the markers sizes"""
        s.r.add_event_handler(cozmo.objects.EvtObjectAppeared, s.handle_object_appeared)
        s.r.add_event_handler(cozmo.objects.EvtObjectDisappeared, s.handle_object_disappeared)
        for action, d in s.actions_library.items():
            if d[0]:
                if not s.r.world.define_custom_cube(d[0], d[1], 50, MARKERS_SIZE, MARKERS_SIZE, True):
                    color_print(f"Marker {action} definition failed!", C_RED)

    def __del__(s):
        """Wait for tasks completion before exiting (needed by the Cozmo SDK to properly exit)"""
        time.sleep(2)

    def convert_obj_type_to_name(s, event_type):
        """Used to get the action name from the Cozmo SDK event type"""
        for action, prop in s.actions_library.items():
            if prop[0] == event_type:
                return action

    ######################################
    # Simple Actions
    def blink(s, blinks):
        """Makes Cozmo's backpack lights blink"""
        blink_speed = 0.05
        for i in range(blinks):
            if i:
                time.sleep(blink_speed)
            s.r.set_all_backpack_lights(cozmo.lights.green_light)
            time.sleep(blink_speed)
            s.r.set_all_backpack_lights(cozmo.lights.blue_light)
            time.sleep(blink_speed)
            s.r.set_all_backpack_lights(cozmo.lights.off_light)

    def raise_forklift(s):
        s.r.move_lift(3)

    def lower_forklift(s):
        s.r.move_lift(-3)

    def turn_left(s):
        s.r.turn_in_place(degrees(90)).wait_for_completed()

    def turn_right(s):
        s.r.turn_in_place(degrees(-90)).wait_for_completed()

    def move_forward(s):
        s.r.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()

    def move_backward(s):
        s.r.drive_straight(distance_mm(-100), speed_mmps(100)).wait_for_completed()

    def speak(s, msg="I'm COZMO'"):
        s.r.say_text(msg).wait_for_completed()

    def anim_won(s):
        s.r.play_anim_trigger(cozmo.anim.Triggers.BuildPyramidThankUser).wait_for_completed()

    def anim_lost(s):
        s.r.play_anim_trigger(cozmo.anim.Triggers.FistBumpLeftHanging).wait_for_completed()
