
#Display
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd2in7_V2
from random import choice 
from oslib import BufferUpdate, Buffer

class Display:
    def __init__(self, epd):
        self.epd = epd
        self.mode = "fast" #slow, fast, partial / slow is unused tho...
        self.fast_count_limit = 6
        self.fast_count = self.fast_count_limit
        self.partial_count = 0
        self.partial_count_limit = 8

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
motb = choice(messages)
qotb = choice(questions)

display = Display(epd2in7_V2.EPD())
print("Starting display...           ", end="\r")
display.epd.init()

def epdDraw(hardware: Display, buffer: Buffer):
    if hardware.mode == "partial": #Safety
        if hardware.fast_count < 6:
            hardware.epd.init_Fast()
            hardware.mode = "fast"

    if hardware.fast_count < 6:
        hardware.epd.display_Fast(buffer.buf)
        hardware.fast_count += 1
    else:
        hardware.epd.init()
        hardware.epd.display(buffer.buf) #A slow, safe update
        hardware.fast_count = 0
        hardware.epd.init_Fast()
    buffer.resetUpdate()

def epdInitPartial(hardware: Display, buffer: Buffer):
    hardware.mode = "partial"
    buffer.resetUpdate()
    hardware.epd.display_Base(buffer.buf)

def epdDrawPartial(hardware: Display, buffer: Buffer, startx: int, starty: int, endx: int, endy: int):
    if(hardware.mode != "partial"):
        epdInitPartial(hardware, buffer)
    if hardware.partial_count == hardware.partial_count_limit: #Refresh n reset our partial for safety
        epdDraw(hardware, buffer)
        epdInitPartial(hardware, buffer)
        hardware.partial_count = 0
        return hardware.partial_count_limit
    hardware.partial_count += 1
    hardware.epd.display_Partial(buffer.buf, startx, starty, endx, endy)
    buffer.resetUpdate()
    return hardware.partial_count_limit - hardware.partial_count

class Input:
    def __init__(self, buttons):
        self.buttons = buttons

    def on_button_press(self, callbacks):
        for button_number, callback in callbacks.items():
            self.buttons[button_number].when_pressed = callback
