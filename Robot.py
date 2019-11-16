import asyncio
import time

import cozmo
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes

from config import MARKERS_SIZE, ACTIONS


class Robot(object):
    def __init__(self, robot):
        self.r = robot
        self.cards = []

    def __del__(self):
        """Wait for tasks completion before exiting (needed by the Cozmo SDK)"""
        time.sleep(2)

    def handle_object_appeared(self, evt, **kw):
        if isinstance(evt.obj, CustomObject):
            print(f"{str(evt.obj.object_type)} appears")
            if self.cards[-1] != evt.obj.object_type:
                self.cards.append(evt.obj.object_type)

    def handle_object_disappeared(self, evt, **kw):
        if isinstance(evt.obj, CustomObject):
            print(f"{str(evt.obj.object_type)} disappear")

    def setup(self):
        self.r.add_event_handler(cozmo.objects.EvtObjectAppeared, self.handle_object_appeared)
        self.r.add_event_handler(cozmo.objects.EvtObjectDisappeared, self.handle_object_disappeared)
        for action in ACTIONS:
            if not self.r.world.define_custom_wall(CustomObjectTypes.CustomType00,
                                    CustomObjectMarkers.Circles3, 297, 210, MARKERS_SIZE, True):
                print(f"Marker {action} definition failed!")

    def launch(self):
        print("Press CTRL-C to quit")
        while True:
            time.sleep(0.1)
