import os
import ctypes
from random import choice, randint, randrange, shuffle
from time import perf_counter, sleep
from threading import Thread

from tkinter import Label, Tk, Frame, Button
import imageio
from moviepy.editor import AudioFileClip
from videoprops import get_video_properties
from PIL import ImageTk, Image, ImageFilter
from config import Configuration

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



def resize(img: Image.Image, screen_size, lowkey_mode) -> Image.Image:
    width, height = screen_size
    size_source = max(img.width, img.height) / min(width, height)
    size_target = randint(30, 70) / 100 if not lowkey_mode else randint(20, 50) / 100
    resize_factor = size_target / size_source
    return img.resize(
        (int(img.width * resize_factor), int(img.height * resize_factor)), Image.LANCZOS
    )

class VideoLabel(Label):
    def load(self, path:str, resized_width:int, resized_height:int):
        self.path = path
        self.configure(background='black')
        self.wid = resized_width
        self.hgt = resized_height
        self.video_properties = get_video_properties(path)
        self.audio = AudioFileClip(self.path)
        self.fps = float(self.video_properties['avg_frame_rate'].split('/')[0]) / float(self.video_properties['avg_frame_rate'].split('/')[1])
        try:
            self.audio_track = self.audio.to_soundarray()
            print(self.audio_track)
            self.audio_track = [[VIDEO_VOLUME*v[0], VIDEO_VOLUME*v[1]] for v in self.audio_track]
            self.duration = float(self.video_properties['duration'])
        except:
            self.audio_track = None
            self.duration = None
        self.video_frames = imageio.get_reader(path)
        self.delay = 1 / self.fps
        
    def play(self):
        from types import NoneType
        if not isinstance(self.audio_track, NoneType):
            try:
                import sounddevice
                sounddevice.play(self.audio_track, samplerate=len(self.audio_track) / self.duration, loop=True)
            except Exception as e:
                print(f'failed to play sound, reason:\n\t{e}')
        while True:
            for frame in self.video_frames.iter_data():
                self.time_offset_start = perf_counter()
                self.video_frame_image = ImageTk.PhotoImage(Image.fromarray(frame).resize((self.wid, self.hgt)))
                self.config(image=self.video_frame_image)
                self.image = self.video_frame_image
                self.time_offset_end = perf_counter()
                sleep(max(0, self.delay - (self.time_offset_end - self.time_offset_start)))

class Video:
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
            print("Starting thread:", lifespan)
            Thread(target=self.live_life, args=(lifespan, ), daemon=True).start()


        self.root.mainloop()

    def get_image(self) -> Image:
        border_wid_const = 5
        tries = 15
        while tries > 0:
            try:
                videos = os.listdir(self.configuration.resource+'\\vid')
                vid_path = self.configuration.resource+'\\vid\\'+choice(videos)
                video_properties = get_video_properties(vid_path)
                image = Image.new('RGB', (video_properties['width'], video_properties['height']))
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
        if denial and not vid_path.endswith("gif"):
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

        label = VideoLabel(self.root)
        label.load(path = vid_path, resized_width = resized_image.width, resized_height = resized_image.height)
        label.pack()
        Thread(target=lambda: label.play(), daemon=True).start()
        
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

        if self.configuration.showcaptions and self.configuration.captions:
            caption_text = self.select_caption(vid_path)
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
        print("sleeping",length)
        sleep(length)
        for i in range(100-self.opacity, 100):
            self.root.attributes('-alpha', 1-i/100)
            sleep(1.5 / 100)
        print("Done")
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
    a = Video(configs)