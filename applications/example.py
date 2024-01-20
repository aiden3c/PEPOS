import ui
import os
import pickle

from oslib import Application, Buffer, Command, nop

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

def init(buf, inputs, app, osData): #We use nop instead of init in this example
    return True

def kill(buf, inputs, app, osData): #We do use this function as our kill though, even though it doesn't do anything. To show you can do both.
    return True

def main(buf, inputs, app, osData):
    ui.draw_text(buf, 5, 5, "Hello world!")
    if inputs[0] == 1:
        ui.draw_text(buf, 5, 15, app.variables["buttonMsg"])
    return True

app = Application("example", nop, main, kill, {"buttonMsg": "Button!"})
