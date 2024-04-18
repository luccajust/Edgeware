from random import choice, randint
import string
from threading import Thread
import tkinter as tk
from tkinter import *
from typing import List
from config import Configuration
import ctypes

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


class Prompt(Toplevel):
    def __init__(self, root):
        super().__init__(root.root)
        self.configuration = root.configuration
        textData = self.configuration.prompts
        submission_text = textData['subtext'] if 'subtext' in textData else 'I Submit <3'
        command_text = textData['commandtext'] if 'commandText' in textData else 'Type for me, slut~'

        self.bind("<KeyPress>", lambda key: self.enterPressed(key))

        label = tk.Label(self, text=command_text, font=("Arial", 12), fg="#ce42f5")
        label.pack()
        selection = choice(textData['moods'])
        self.txt = choice(textData[selection])

        wid = int(root.root.winfo_screenwidth() / 4)
        hgt = int(root.root.winfo_screenheight() / 5)

        textLabel = Label(self, text=self.txt, wraplength=wid, font=("Arial", 15) )
        textLabel.pack()

        self.geometry('%dx%d+%d+%d' % (wid, hgt, 2*wid - wid / 2, hgt - hgt / 2))
        self.overrideredirect(1)
        self.frame = Frame(self, borderwidth=2, relief=RAISED)
        self.frame.pack_propagate(True)
        self.wm_attributes('-topmost', 1)

        self.inputBox = Text(self)
        self.inputBox.pack()

        subButton = Button(self, text=submission_text, command=lambda: self.checkTotal())
        subButton.place(x=wid - 5 - subButton.winfo_reqwidth(), y=hgt - 5 - subButton.winfo_reqheight())

        monitor_data = monitor_areas()
        data_list = list(choice(monitor_data)[2])
        locX = randint(data_list[0], data_list[2] - (wid))
        locY = randint(data_list[1], max(data_list[3] - (hgt), 0))
        self.geometry(f'{wid + 4}x{hgt + 4}+{locX}+{locY}')

    def enterPressed(self, key):
        if key.keysym == 'Return':
            self.checkTotal()

    def checkTotal(self):
        # jaccard_similarity
        a = remove_punctuation(self.txt)
        b = remove_punctuation(self.inputBox.get(1.0, "end-1c"))
        intersection_cardinality = len(set.intersection(*[set(a), set(b)]))
        union_cardinality = len(set.union(*[set(a), set(b)]))
        similarity = intersection_cardinality/float(union_cardinality)

        if similarity >= 1.0 - 0.033*self.configuration.promptmistakes:
            print("Destroy")
            self.destroy()
            


def remove_punctuation(text):
    return ''.join([char for char in text if char not in string.punctuation]).lower()


if __name__ == '__main__':
    config = Configuration.load_configuration()
    config.load_jsons()

    root = Tk()
    root.withdraw()

    print("Tests")

    txt = Prompt(root, config)
    txt = Prompt(root, config)

    root.mainloop()
    print("Exited")