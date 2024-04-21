from multiprocessing import Process, active_children
from threading import Thread
from time import sleep
from tkinter import Tk
from typing import Callable, List
from config import Configuration
from random import uniform
from prompt import Prompt
from video import Video
from web import web
from audio import audio
from popup import Image


class Edgeware:
    """Main class that handles everything in the game."""

    def __init__(self) -> None:
        """Constructor of the main Edgeware class"""
        self.configuration: Configuration = Configuration.load_configuration()
        self.configuration.load_jsons()
        self.start()
        
    
    def random_event(self) -> Callable:
        print("Calling random event...")
        probabilities = {
            audio: 0,
            self.popup: 1,
            self.prompt: 0,
            self.vid: 0,
            self.web: 0,
        }
        total_probability = sum(probabilities.values())
        random_num = uniform(0, total_probability)
        cumulative_probability = 0
        for event, probability in probabilities.items():
            cumulative_probability += probability
            if random_num <= cumulative_probability:
                return event

    def popup(self):
        """Creates Popup with an Image or a Gif"""
        children = active_children()
        if len(children) > 20: return # CAP AT 20 TODO: Change to config
        thread = Process(target=Image, args=(self.configuration,))
        thread.start()

    def web(self):
        web(self.configuration.web)


    def prompt(self):
        print("Prompt")
        Prompt(self)

    def vid(self):
        children = active_children()
        if len(children) > 20: return # CAP AT 20 TODO: Change to config
        proc = Process(target=Video, args=(self.configuration,))
        proc.start()

    def panic(self):
        """Currently unused"""
        active = active_children()
        for child in active:
            child.kill()
        for child in active:
            child.join()
        

    def start(self):
        try:
            while True:
                sleep(self.configuration.delay/1000)
                event = self.random_event()
                event()
        except KeyboardInterrupt:
            print("Panic! Exiting...")
            self.panic()
            print("Done!")


if __name__ == "__main__":
    main = Edgeware()