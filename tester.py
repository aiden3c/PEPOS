import ui
import os
import pickle
from random import randint, choice

from oslib import Application, Buffer, Command

def load_settings(filename):
    filepath = os.path.join('config', filename)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return None
def save_settings(filename, data):
    filepath = os.path.join('config', filename)
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)

def nop(*args):
    pass

def main(buf, inputs, app, osData):
    words = ["yo", "hi", "ye", "69", ":3", ":)", "B)"]
    word = choice(words)
    if inputs[0] == 1:
        update = Buffer(25, 25, 0)
        ui.draw_text(update, 5, 5, word, fill=255)
        x = randint(0, buf.width-update.width)
        y = randint(0, buf.height-update.height)
        osData["modules"].epdDrawPartial(buf, update, x, y, x+update.width, y+update.height)
    return Command("setFlag", "noDraw", True)

testerApp = Application("tester", nop, main, nop, {})