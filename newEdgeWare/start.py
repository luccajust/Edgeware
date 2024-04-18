from multiprocessing import Process
from threading import Thread
from time import sleep
from tkinter import Tk
from typing import List
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
        self.children: List[Process] = []
        self.root = Tk()
        self.root.withdraw()
        Thread(target=self.start()).start()
        self.root.mainloop()
        
    
    def random_event(self) -> callable:
        print("Calling random event...")
        probabilities = {
            audio: self.configuration.audiomod / 100,
            self.popup: self.configuration.popupmod / 100,
            self.prompt: self.configuration.promptmod / 100,
            self.vid: self.configuration.vidmod / 100,
            self.web: self.configuration.webmod / 100,
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
        if len(self.children) > 20: return # CAP AT 20 TODO: Change to config
        thread = Thread(target=Image, args=(self,))
        self.children.append(thread)
        thread.start()

    def web(self):
        web(self.configuration.web)


    def prompt(self):
        print("Prompt")
        Prompt(self)

    def vid(self):
        if len(self.children) > 20: return # CAP AT 20 TODO: Change to config
        proc = Process(target=Video, args=(self,))
        self.children.append(proc)
        proc.start()

    def panic(self):
        """Currently unused"""
        for i in self.children:
            i.terminate()

    def update_children(self):
        for i in self.children:
            if not i.is_alive():
                self.children.remove(i)

    def start(self):
        while True:
            self.update_children()
            sleep(self.configuration.delay/1000)
            event = self.random_event()
            event()
            


if __name__ == "__main__":
    main = Edgeware()
    print("Staring...")
