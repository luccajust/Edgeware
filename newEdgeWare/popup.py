import os
from threading import Thread
from time import sleep
import tkinter as tk
from tkinter import Tk, Frame, Label, Button, RAISED

import pathlib
from videoprops import get_video_properties
from PIL import Image as PilImage, ImageFilter, ImageTk
from random import randint, randrange, choice, shuffle
from itertools import count, cycle
import ctypes

from config import Configuration

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from start import Edgeware

PATH = str(pathlib.Path(__file__).parent.absolute())
user = ctypes.windll.user32

def get_monitors():
    retval = []
    CBFUNC = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.POINTER(RECT),
        ctypes.c_double,
    )

    def cb(hMonitor, hdcMonitor, lprcMonitor, dwData):
        r = lprcMonitor.contents
        data = [hMonitor]
        data.append(r.dump())
        retval.append(data)
        return 1

    cbfunc = CBFUNC(cb)
    temp = user.EnumDisplayMonitors(0, 0, cbfunc, 0)
    return retval


def monitor_areas():
    retval = []
    monitors = get_monitors()
    for hMonitor, extents in monitors:
        data = [hMonitor]
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        mi.rcMonitor = RECT()
        mi.rcWork = RECT()
        res = user.GetMonitorInfoA(hMonitor, ctypes.byref(mi))
        data.append(mi.rcMonitor.dump())
        data.append(mi.rcWork.dump())
        retval.append(data)
    return retval


class RECT(ctypes.Structure):  # rect class for containing monitor info
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

    def dump(self):
        return map(int, (self.left, self.top, self.right, self.bottom))


class MONITORINFO(
    ctypes.Structure
):  # unneeded for this, but i don't want to rework the entire thing because i'm stupid
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", ctypes.c_ulong),
    ]


def resize(img: PilImage.Image, screen_size, lowkey_mode) -> PilImage.Image:
    width, height = screen_size
    size_source = max(img.width, img.height) / min(width, height)
    size_target = randint(30, 70) / 100 if not lowkey_mode else randint(20, 50) / 100
    resize_factor = size_target / size_source
    return img.resize(
        (int(img.width * resize_factor), int(img.height * resize_factor)), PilImage.LANCZOS
    )

class GifLabel(tk.Label):
    def load(self, path:str, resized_width:int, resized_height:int, delay:int=75, back_image:PilImage.Image=None):
        self.image = PilImage.open(path)
        self.configure(background='black')
        self.frames:list[ImageTk.PhotoImage] = []
        self.delay = delay
        try:
            for i in count(1):
                hold_image = self.image.resize((resized_width, resized_height), PilImage.BOX)
                if back_image is not None:
                    hold_image, back_image = hold_image.convert('RGBA'), back_image.convert('RGBA')
                    hold_image = PilImage.blend(back_image, hold_image, 0.2)
                self.frames.append(ImageTk.PhotoImage(hold_image.copy()))
                self.image.seek(i)
        except Exception as e:
            print(f'{e}')
            print(f'Done register frames. ({len(self.frames)})')
        self.frames_ = cycle(self.frames)

    def next_frame(self):
        if self.frames_:
            self.config(image=next(self.frames_))
            self.after(self.delay, self.next_frame)


class Image:
    def __init__(self, config: Configuration) -> None:
        self.configuration = config
        self.opacity = 100
        self.root = Tk()
        self.root.bind("<KeyPress>", lambda key: self.panic_handler(key))
        self.root.configure(bg="black")
        self.root.overrideredirect(1)
        self.root.frame = Frame(self.root)
        self.root.wm_attributes("-topmost", 1)

        self.load_configs()

        image = self.get_image()

        submission = ['Yes, I Submit!', 'I Submit <3']
        if isinstance(self.configuration.captions['subtext'], list):
            submission.extend(self.configuration.captions['subtext'])
        else:
            submission.append(self.configuration.captions['subtext'])

        submit_button = Button(self.root, text=choice(submission), command=self.stop)
        submit_button.place(x=image.width - 5 - submit_button.winfo_reqwidth(), y=image.height - 5 - submit_button.winfo_reqheight())

        self.root.attributes('-alpha', self.opacity / 100)

        if self.configuration.timeoutpopups or self.configuration.lktoggle:
            lifespan = self.configuration.popuptimeout if not self.configuration.lktoggle else self.configuration.delay / 1000
            Thread(target=self.live_life, args=(lifespan, ), daemon=True).start()


        self.root.mainloop()

    def get_image(self) -> PilImage.Image:
        border_wid_const = 5
        tries = 15
        while tries > 0:
            try:
                images = os.listdir(self.configuration.resource+'\\img')
                img_path = self.configuration.resource+'\\img\\'+choice(images)
                image = PilImage.open(img_path)
                break
            except Exception as e:
                tries -= 1

        monitor_data = monitor_areas()
        data_list = list(monitor_data[randrange(0, len(monitor_data))][2]) #TODO: Change to choice
        screen_size = (data_list[2] - data_list[0], data_list[3] - data_list[1])
        resized_image = resize(image, screen_size, self.configuration.lktoggle)
        denial = (
            self.configuration.denialmode
            and randint(1, 100) <= self.configuration.denialchance
        )

        # APPLY BLUR IF DENIAL
        if denial and not img_path.endswith("gif"):
            blur_modes = [
                ImageFilter.GaussianBlur(5),
                ImageFilter.GaussianBlur(10),
                ImageFilter.GaussianBlur(20),
                ImageFilter.BoxBlur(5),
                ImageFilter.BoxBlur(10),
                ImageFilter.BoxBlur(20),
            ]
            shuffle(blur_modes)
            resized_image = resized_image.filter(blur_modes.pop())
        
        self.photoimage_image = ImageTk.PhotoImage(resized_image)
        image.close()

        if img_path.endswith('gif'):
            label = GifLabel(self.root)
            label.load(path=img_path,
                       resized_width = resized_image.width, 
                       resized_height = resized_image.height)
            label.pack()
        else:
            if self.configuration.popupsubliminals and randint(0,100) <= 20: #TODO Add subliminal chance
                label = GifLabel(self.root)
                #TODO Extract paths from resources
                #TODO Add resources validator
                subliminal_path = os.path.join(PATH, 'default_assets', 'default_spiral.gif')

                if os.path.exists(os.path.join(self.configuration.resource, 'subliminals')):
                    subliminal_options = [file for file in os.listdir(os.path.join(self.configuration.resource, 'subliminals')) if file.lower().endswith('.gif')]
                    if len(subliminal_options) > 0:
                        subliminal_path = os.path.join(self.configuration.resource, 'subliminals', str(choice(subliminal_options)))

                label.load(subliminal_path, self.photoimage_image.width(), self.photoimage_image.height(), back_image=resized_image)
                label.pack()
                label.next_frame()
            else:
                label = Label(self.root, image=self.photoimage_image, bg='black')
                label.pack()
        
            if denial:
                deny_options = self.configuration.captions.get('denial')
                if deny_options is None or len(self.configuration.captions['denial']) == 0:
                    deny_text = 'Not for you~'
                else:
                    deny_text = choice(self.configuration.captions['denial'])
                
                denyLabel = Label(label, text=deny_text)
                denyLabel.place(x=int(resized_image.width / 2) - int(denyLabel.winfo_reqwidth() / 2),
                                y=int(resized_image.height / 2) - int(denyLabel.winfo_reqheight() / 2))
        
        locX = randint(data_list[0], data_list[2] - (resized_image.width))
        locY = randint(data_list[1], max(data_list[3] - (resized_image.height), 0))

        if self.configuration.lktoggle:
            if self.configuration.lkcorner == 4:
                self.configuration.lkcorner = randrange(0, 3)
            if self.configuration.lkcorner == 0:
                locX = data_list[2] - (resized_image.width)
                locY = 0
            elif self.configuration.lkcorner == 1:
                locX = 0
                locY = 0
            elif self.configuration.lkcorner == 2:
                locX = 0
                locY = data_list[3] - (resized_image.height)
            elif self.configuration.lkcorner == 3:
                locX = data_list[2] - (resized_image.width)
                locY = data_list[3] - (resized_image.height)
        
        self.root.geometry(f'{resized_image.width + border_wid_const - 1}x{resized_image.height + border_wid_const - 1}+{locX}+{locY}')
    
        if img_path.endswith("gif"):
            label.next_frame()

        if self.configuration.showcaptions and self.configuration.captions:
            caption_text = self.select_caption(img_path)
            if caption_text is not None:
                captionLabel = Label(self.root, text=caption_text, wraplength=resized_image.width - border_wid_const)
                captionLabel.place(x=5, y=5)
        
        return resized_image
    
    def select_caption(self, img_path:str) -> str:
        options = []
        captions = self.configuration.captions
        for i in captions['prefix']:
            if i in img_path:
                options.extend(captions[i])
        options.extend(captions['default'])
        return choice(options)

    def live_life(self, length:int):
        sleep(length)
        for i in range(100-self.opacity, 100):
            self.root.attributes('-alpha', 1-i/100)
            sleep(1.5 / 100)
        self.stop()
        

    def load_configs(self):
        self.configuration.captions = self.configuration.captions
        try:
            self.submission_text = self.configuration.captions['subtext']
        except:
            print('will use default submission text')


    def stop(self):
        self.root.destroy()
    
    def panic_handler(self, key):
        key_condition = self.configuration.panicbutton in [key.keysym, key.keycode]
        if key_condition:
            os.startfile('panic.pyw')


if __name__ == "__main__":
    configs = Configuration.load_configuration()
    configs.load_jsons()
    a = Image(configs)
    
