# Library : 
# http://cozmosdk.anki.com/docs/

"""
       self.robot.world.request_nav_memory_map(frequency_s=2)
        self.set_to_seek_position()	
        origin = self.robot.pose
        self.robot.go_to_pose(Pose(500,0,0,angle_z=degrees(0))).wait_for_completed()
#        map = self.robot.world.nav_memory_map
#        self.robot.go_to_pose(Pose(map.center.x,map.center.y,map.center.z,angle_z=degrees(0))).wait_for_completed()
#        self.robot.go_to_pose(Pose(0,0,0,angle_z=degrees(0))).wait_for_completed()
        interm = self.robot.pose
        self.robot.go_to_pose(Pose(0,200,0,angle_z=degrees(0))).wait_for_completed()
        self.robot.go_to_pose(interm).wait_for_completed()
        self.robot.go_to_pose(origin).wait_for_completed()
        self.robot.say_text("I am here my friend !").wait_for_completed()"""

import asyncio
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id
from PIL import Image

class Robot(object):
    def __init__(self, robot):
        self.robot = robot
        self.cubeList = [] # ## List of the cub --> positions included inside the 3 cubes objects
        self.cube_target = None
        self.face_target = None 
        self.pos_when_face = None # ## The position of the robot when it is communicaing (can't register the face position)
        self.cards = []
        self.poseRecord = [] # ## Array of the positions reached by cozmo associated to their timestamp
        self.interactLvL = 0 # ## Lvl of interaction we want for the session

    def __del__(self):
        time.sleep(2)  # Wait for tasks completion before exiting

		# ## Function makes cozmo node
    def node(self,count):
        if self.interactLvL>0 and self.interactLvL <2:
            j=0
            while j<count:
                self.robot.set_head_angle(degrees(-10),100.0,80.0).wait_for_completed()
                self.robot.set_head_angle(degrees(10),100.0,80.0).wait_for_completed()
                j+=1

# ## Reaction for winning				
    def cozmo_winner(self, node_number):
        self.robot.set_lift_height(height=90).wait_for_completed()
        self.node(node_number)
        self.robot.set_lift_height(height=0).wait_for_completed()	

# ## Function to print image on cozmo face 
    def show_image(self,image_name):
        image = Image.open(image_name)
        image = image.resize(cozmo.oled_face.dimensions(),Image.NEAREST)
        cos_face = cozmo.oled_face.convert_image_to_screen_data(image, invert_image=False, pixel_threshold=127)
        self.robot.display_oled_face_image(cos_face, 50.0*1000.0,True)		

# ## Function to associate position to timestamp and add it to the recoed		
    def record_pose(self):
        self.poseRecord.append([self.robot.pose,time.time()])

# ## Function to reach a cube position and save it		
    def reach_cube(self,cube):
        action = self.robot.go_to_object(cube, distance_mm(50.0)).wait_for_completed()
        self.record_pose()

# ## Function to move to the position it is when communicating for the first time and save it in (pos_when_face)		
    def moveToUser(self,face):
        action = self.robot.turn_towards_face(face).wait_for_completed()
        action = self.robot.drive_straight(distance_mm(100),speed_mmps(50)).wait_for_completed()
        self.pos_when_face = self.robot.pose
        self.record_pose()

# ## Function to map the world : map the 3 cubes and add each one in an array, then look for a face	
    def mapWorld(self):
        cube = None
        previousCube = None
        cubeFound = 0
        self.robot.set_head_angle(degrees(0)).wait_for_completed()
        if self.interactLvL > 0:
            self.robot.say_text("Where are cubes").wait_for_completed()

        discover = self.robot.turn_in_place(degrees(360),speed=degrees(10))
        try:
            while cubeFound < 3 and discover.is_running:
                cube = self.robot.world.wait_for_observed_light_cube(timeout=120)
                if cube is not None and cube != previousCube:
                    self.cubeList.append(cube)
                    previousCube = cube
                    cubeFound+=1
#                    if self.interactLvL > 0:
#                        self.robot.say_text("Here").wait_for_completed()
        except asyncio.TimeoutError:
            print("Didn't find any cube :-(")
        finally:
            discover.abort()
            self.robot.set_head_angle(degrees(30)).wait_for_completed()
            if self.interactLvL > 1:
                    self.robot.say_text("Who wanna play ?").wait_for_completed()
            self.seek_player(60)
            if self.face_target is not None:
                if self.interactLvL > 1:
                    self.robot.say_text("Here you are").wait_for_completed()
                self.moveToUser(self.face_target)
                self.node(3)       
                if self.interactLvL == 1:
                    self.robot.say_text("Hello! ").wait_for_completed()
                elif self.interactLvL == 2:
                    self.robot.say_text("Hello I'm Bob! ").wait_for_completed()
                    self.cozmo_winner(0)

# ##  Global function created : map the world and then navigate to every cube, then face, then go back to its original position					
    def navWorld(self):
        if self.interactLvL == 0:
            self.robot.say_text("").wait_for_completed()
        else:
            self.robot.say_text("Let's go").wait_for_completed()
        self.record_pose()
        self.mapWorld()
        for cube in self.cubeList:
            self.reach_cube(cube)
            if self.interactLvL > 0:			
                self.node(1)
        self.robot.go_to_pose(self.pos_when_face).wait_for_completed()
        if self.interactLvL > 0:			
            self.robot.say_text("Finished! ").wait_for_completed()
            if self.interactLvL ==2:
                self.show_image("./cup.png")
                self.cozmo_winner(1)
                self.robot.say_text("Thanks for playing ").wait_for_completed()
            self.robot.say_text("Let's sleep ! ").wait_for_completed()
        self.robot.go_to_pose(self.poseRecord[0][0]).wait_for_completed()       		
        		
    """def launch(self):
        while 42:
            self.seek_player(timeout=15)			
            if not self.face_target:
                print("Could not find a player")
                self.robot.play_anim_trigger(cozmo.anim.Triggers.NothingToDoBoredIdle).wait_for_completed()
            else:
                self.robot.say_text("Let's play a game!").wait_for_completed()
                self.robot.say_text("Show me control cards and I'll execute their actions in order").wait_for_completed()
                self.robot.say_text("Try to make me stack a cube on top on another one").wait_for_completed()
                self.robot.say_text("Let's go! Show me the actions you want me to execute!").wait_for_completed()
                break"""

    def seek_player(self, timeout):
        start_time = time.time()
        while ((time.time() - start_time) < timeout) and not self.face_target:
            if self.face_target and self.face_target.is_visible:
                self.robot.turn_towards_face(self.face_target).wait_for_completed()
                break
            else:
                tmp = self.robot.turn_in_place(degrees(36))
                self.face_target = self.find_face_in_fov(2)  # Check for faces during 2 secs
            tmp.wait_for_completed()

    def find_face_in_fov(self, timeout=30):
        face = None
        try:
            face = self.robot.world.wait_for_observed_face(timeout)
        except asyncio.TimeoutError:
            print("Couldn't find a face.")
 #       else:
 #           self.robot.play_anim_trigger(cozmo.anim.Triggers.AcknowledgeFaceNamed).wait_for_completed()
        return face

    """def set_to_seek_position(self):
        #Move lift down, tilt head up, turn around to find something
        action1 = self.robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE / 2)
        action2 = self.robot.set_lift_height(0, in_parallel=True)
        action1.wait_for_completed()
        action2.wait_for_completed()"""
