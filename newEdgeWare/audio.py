from playsound import playsound
import os
import pathlib
from multiprocessing import Process
from random import randrange

PATH = str(pathlib.Path(__file__).parent.absolute())


PROCESS:Process = None

AUDIO = []
try:
    for aud in os.listdir(PATH + '\\resource\\aud\\'):
        AUDIO.append(PATH + '\\resource\\aud\\' + aud)
except: pass


def _audio():
    playsound(AUDIO[randrange(len(AUDIO))])
    
def audio():
    global PROCESS
    if PROCESS is not None:
        return
    PROCESS = Process(target=_audio)
    PROCESS.start()

def stop_audio():
    global PROCESS
    if PROCESS is None: return None
    PROCESS.terminate()

if __name__ == "__main__":
    audio()
    input("Press enter to stop")
    stop_audio()
