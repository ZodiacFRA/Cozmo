import asyncio
import time
import random
import os
import math

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
from cozmo.objects import CustomObjectMarkers as co_markers
from cozmo.objects import CustomObjectTypes as co_types
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from utils import *


class Robot(object):
    def __init__(s, robot):
        s.r = robot
        s.talkative = True
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

            "do_interactive_game": [co_types.CustomType09, co_markers.Circles4, None],
            "do_autonomous_game": [co_types.CustomType10, co_markers.Diamonds2, None],
            "do_map_discovery": [co_types.CustomType12, co_markers.Triangles5, None]
        }
        s.lose_animations = [
            cozmo.anim.Triggers.CubePounceGetUnready,
            cozmo.anim.Triggers.PeekABooGetOutSad,
            cozmo.anim.Triggers.CodeLabLose,
            cozmo.anim.Triggers.CubePounceLoseHand,
            cozmo.anim.Triggers.CubePounceLoseSession,
            cozmo.anim.Triggers.MemoryMatchCozmoLoseHand
        ]
        s.add_markers_detection()
        # Game data
        s.game_type = None
        s.instructions = []
        s.player = None
        s.player_name = input("Player name: ")
        s.cubes = None
        s.game_log = {"Positions": []}

        s.last_pose = None
        s.fig = None


    def launch(s):
        s.init_plot()
        while 42:
            s.instructions.clear()
            s.game_type = None
            s.player = None
            s.cubes = None
            s.game_log = {"Positions": []}
            s.record_pos("Game Start")
            s.seek_player()  # Will loop until a player is found
            s.plot_pose()
            # Game type handling
            tmp_time = time.time()
            if "do_autonomous_game" not in s.instructions and "do_interactive_game" not in s.instructions and "do_map_discovery" not in s.instructions:
                s.speak("Do you want to play with me? Or do I do it on my own?")
            while time.time() - tmp_time < 30:
                if "do_autonomous_game" in s.instructions:
                    s.r.play_anim_trigger(random.choice(s.lose_animations)).wait_for_completed()
                    s.game_log["Game Type"] = "Autonomous"
                    s.game_type = ROBOT
                    s.speak("Ok, I will do it on my own")
                    break
                elif "do_interactive_game" in s.instructions:
                    s.anim_won()
                    s.game_log["Game Type"] = "Interactive"
                    s.game_type = HUMAN
                    break
                elif "do_map_discovery" in s.instructions:
                    s.game_log["Game Type"] = "Discovery"
                    s.game_type = DISCOVERY
                    break
                time.sleep(0.5)
            else:  # No instructions, quit
                s.speak("Good bye!")
                return

            s.instructions.clear()

            flag = False
            if s.game_type == HUMAN:
                s.get_instructions()
                s.game_log["Execution start time"] = time.time()
                flag = s.execute_instructions()
                s.game_log["Execution end time"] = time.time()
            elif s.game_type == ROBOT: # Autonomous gameplay
                s.game_log["Execution start time"] = time.time()
                flag = s.stack_cubes()
                s.game_log["Execution end time"] = time.time()
            elif s.game_type == DISCOVERY:
                s.game_log["Execution start time"] = time.time()
                flag = s.detect_cube(3)
                s.game_log["Execution end time"] = time.time()

            if flag:
                s.anim_won()
                action = s.r.go_to_pose(s.game_log["Positions"][1][2])
                while action.is_running:
                    s.plot_pose()
                s.r.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
                if s.game_type == HUMAN:
                    s.speak("We did it!")
                else:
                    s.speak("I did it!")
            else:
                s.anim_lost()
                action = s.r.go_to_pose(s.game_log["Positions"][1][2])
                while action.is_running:
                    s.plot_pose()
                s.r.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
                if s.game_type == HUMAN:
                    s.speak("We failed!")
                else:
                    s.speak("I failed!")


            # Log all game data and reset it
            s.write_game_log(flag)
            plt.savefig(f"./images/{s.player_name}_{time.time()}.png", bbox_inches='tight')
            plt.clf()

    ######################################
    # Complex Actions
    def approach_cube(s):
        """For player game, in this case"""
        if not s.cubes:
            color_print("Cozmo does not remember any cube!", C_RED)
        else:
            gotoCube = s.r.go_to_object(s.cubes[0], distance_mm(50.0))
            while gotoCube.is_running:
                s.plot_pose()

    def detect_cube(s, wanted_cube_nbr=1):
        lookaround = s.r.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        # time.sleep(5)
        s.cubes = s.r.world.wait_until_observe_num_objects(num=wanted_cube_nbr, object_type=cozmo.objects.LightCube, timeout=60)
        lookaround.stop()
        if len(s.cubes) < wanted_cube_nbr:
            return color_print(f"Error: need {wanted_cube_nbr} Cubes but only found: {len(s.cubes)} Cube(s)", C_RED)
        else:
            for cube in s.cubes:
                plt.plot([cube.pose.position.x],[cube.pose.position.y],'rs', label='Cubes')
                s.fig.canvas.draw()

        return True

    def pickup_cube(s, cube_obj=None, num_retries=4):
        s.r.stop_all_motors()
        print("pickup cube", s.cubes)
        if not cube_obj:
            cube_obj = s.cubes[0]
        action = s.r.pickup_object(cube_obj, num_retries=num_retries)
        while action.is_running:
            s.plot_pose()
        return action

    def place_on_object(s, cube_obj=None, num_retries=3):
        s.r.stop_all_motors()
        if not cube_obj:
            print("pickup cube", s.cubes)
            cube_obj = s.cubes[0]
        action = s.r.place_on_object(cube_obj, num_retries=num_retries)
        while action.is_running:
            s.plot_pose()
        return action

    def stack_cubes(s):
        """For autonomous game"""
        if s.detect_cube(2):
            # Try and pickup the 1st cube
            action = s.pickup_cube(s.cubes[0], num_retries=3)
            if action.has_failed:
                code, reason = action.failure_reason
                if action.result == cozmo.action.ActionResults.BAD_OBJECT:
                    pass
                if action.result == cozmo.action.ActionResults.CANCELLED_WHILE_RUNNING:
                    s.speak("I can't see enough cubes")
                return color_print(f"Pickup Cube failed! code: {code}\nreason: {reason}\nresult: {action.result}", C_RED)

            # Now try to place that cube on the 2nd one
            action = s.place_on_object(s.cubes[1], num_retries=3)
            if action.has_failed:
                code, reason = action.failure_reason
                if action.result == cozmo.action.ActionResults.BAD_OBJECT:
                    s.stack_cubes()
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
                plt.plot([s.player.pose.position.x],[s.player.pose.position.y],'k*', label='Player')
                plt.autoscale(enable=True,axis='both',tight=None)
                s.fig.canvas.draw()
                return
            else:
                color_print("Player not found after 30 seconds, retrying...", C_RED)
            s.r.play_anim_trigger(cozmo.anim.Triggers.NothingToDoBoredIdle).wait_for_completed()

    ######################################
    # Utils
    def write_game_log(s, outcome):
        f = None
        if os.path.exists("./Cozmo_games_data.tsv"):
            f = open("./Cozmo_games_data.tsv", 'a', encoding="utf-8")
        else:
            f = open("./Cozmo_games_data.tsv", 'w', encoding="utf-8")
            f.write("Player name\tGame type\tPositions\tOutcome\tExecution time\tInstructions\n")
        positions = [f"{record[0]},{record[1]},{record[2]}" for record in s.game_log["Positions"]]
        f.write(f"""{s.player_name}\t{s.game_type}\t{';'.join(positions)}\t{outcome}\t{s.game_log["Execution end time"] - s.game_log["Execution start time"]}\t{';'.join(s.instructions)}\n""")
        f.close()

    def record_pos(s, event):
        """Logs the time, event (string) and pose of the robot when called"""
        s.game_log["Positions"].append((time.time(), event, s.r.pose))
        # print("Pos reg: ",s.r.pose.position.x,";",s.r.pose.position.y)

    def init_plot(s):
        s.fig = plt.gcf()
        plt.xlabel('X position')
        plt.ylabel('Y position')
        plt.title('Map Evolution')

        cubes = mpatches.Patch(color='red', label='cubes')
        Face = mpatches.Patch(color='black', label='Face')
        Bob_Path = mpatches.Patch(color='cyan', label='Bob Path')
        Bob_Position = mpatches.Patch(color='blue', label='Bob Position')
        plt.legend(handles=[cubes, Face, Bob_Path, Bob_Position])

        s.fig.show()
        s.fig.canvas.draw()
        plt.autoscale(enable=True,axis='both',tight=None)

    def plot_pose(s):
        if s.last_pose is not None:
            plt.plot([s.last_pose.position.x],[s.last_pose.position.y],'c.', label='Bob Path')
        s.last_pose = s.r.pose
        plt.plot([s.last_pose.position.x],[s.last_pose.position.y],'b.', label='Bob Position')
        plt.autoscale(enable=True,axis='both',tight=None)
        s.fig.canvas.draw()

    def get_instructions(s):
        """Wait for the player to show the instructions and
        store them, returns when the player shows the EOT marker"""
        s.speak("You can give me the instructions now!")
        while not len(s.instructions) or s.instructions[-1] != "EOT":
            time.sleep(0.5)
        s.speak("Let's go!")
        color_print(f"All {len(s.instructions)} instructions have been stored and will now be executed by Cozmo", C_GREEN)
        s.instructions.pop()
        # "Easy mode" implementation, to prevent cozmo failing the game even if the player did everything properly
        for i in range(len(s.instructions)):
            if s.instructions[i] == "approach_cube":
                if i == 0 or s.instructions[i - 1] != "detect_cube":
                    s.instructions.insert(i, "detect_cube")
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
        flag = 0
        for instruction in s.instructions:
            if s.actions_library[instruction][2]:
                color_print(f"Executing {instruction}", C_BLUE)
                action = s.actions_library[instruction][2]()
                s.record_pos(instruction)
                if hasattr(action, "has_failed") and not action.has_failed:
                    flag += 1
        return flag == 2

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
                # s.speak(action_name.replace('_', ' '))
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
        action = s.r.turn_in_place(degrees(90))
        while action.is_running:
            s.plot_pose()

    def turn_right(s):
        action = s.r.turn_in_place(degrees(-90))
        while action.is_running:
            s.plot_pose()

    def move_forward(s):
        action = s.r.drive_straight(distance_mm(100), speed_mmps(100))
        while action.is_running:
            s.plot_pose()

    def move_backward(s):
        action = s.r.drive_straight(distance_mm(-100), speed_mmps(100))
        while action.is_running:
            s.plot_pose()

    def speak(s, msg="I'm COZMO"):
        if s.talkative:
            s.r.say_text(msg).wait_for_completed()
        else:
            color_print(msg, C_BLUE)

    def anim_won(s):
        s.r.play_anim_trigger(cozmo.anim.Triggers.BuildPyramidThankUser).wait_for_completed()

    def anim_lost(s):
        s.r.play_anim_trigger(cozmo.anim.Triggers.FistBumpLeftHanging).wait_for_completed()
