
#Display
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd2in7_V2
from random import randint
from oslib import BufferUpdate, Buffer

class Display:
    def __init__(self, epd, mode):
        self.epd = epd
        self.mode = mode
        

messages = [
    "You are appreciated!",
    "Hope you are well! :3",
    "Thank goodness you're here!",
    "Have a lot of fun...",
    "Huh? I'm awake!",
    "We have a calendar!",
    "Stay hydrated!",
    "Remember to write!",
    "Good morning, day, evening, or night!"
]

#qotb question of the boot. short questions to get you thinking
questions = [
    "What are you thankful for?",
    "What are you looking forward to?",
    "What are you excited about?",
    "How are you feeling?",
    "What are you thinking about?",
    "When did you meditate last?",
    "Make sure to eat!",
    "Have you slept well?",
    "What's today's plan?",
    "What's new?",
    "What's up?",
    "How's it going?",
    "How are you?",
    "Do you have a happy place?",
    "What are you learning?",
    "What are you writing?",
    "What are you reading?",
    "What are you creating?"
]
motb = messages[randint(0, len(messages) - 1)]
qotb = questions[randint(0, len(questions) - 1)]

epd = epd2in7_V2.EPD()
print("Starting display...           ", end="\r")
epd.init()

def epdDrawFresh(data):
    global fast_count
    global partial_count
    epd.init()
    epd.display(data)
    fast_count = 0
    partial_count = 0

epdState = "fast"
fast_count = 6
partial_count = 0
partial_count_limit = 8
def epdDraw(data, fix=False):
    global fast_count
    global epdState
    if epdState != "fast" and epdState != "slow":
        if fast_count < 6:
            epd.init_Fast()
            epdState = "fast"

    if fast_count < 6:
        epd.display_Fast(data)
        fast_count += 1
    else:
        epd.init()
        epd.display(data)
        fast_count = 0
        epd.init_Fast()

def epdInitPartial(buf: Buffer):
    global epdState
    epdState = "partial"
    buf.resetUpdate()
    epd.display_Base(buf.buf)

def epdDrawPartial(startBuf: Buffer, startx: int, starty: int, endx: int, endy: int):
    global partial_count
    global epdState
    if(epdState != "partial"):
        epdInitPartial(startBuf)
        epdState = "partial"
    if partial_count == partial_count_limit:
        epdDrawFresh(startBuf.buf)
        return partial_count_limit
    partial_count += 1
    epd.display_Partial(startBuf.buf, startx, starty, endx, endy)
    startBuf.resetUpdate()
    return partial_count_limit - partial_count

class Display:
    #Refresh entire screen, determining whether it should be a fast draw or not
    def draw(self, data):
        epdDraw(data)

class Input:
    def __init__(self, buttons):
        self.buttons = buttons

    def on_button_press(self, callbacks):
        for button_number, callback in callbacks.items():
            self.buttons[button_number].when_pressed = callback

#Move this to oslib after /the/ bug fix
import threading
class Timer:
    def __init__(self, time, callback, repeat = False):
        self.callback = callback
        self.repeat = repeat
        self.timer = threading.Timer(time, self.run_callback)

    def run_callback(self):
        self.callback()
        if self.repeat:
            self.timer.start()
        else:
            self.stop()

    def start(self):
        self.timer.cancel()
        self.timer.start()
        
    def stop(self):
        self.timer.cancel()
    
