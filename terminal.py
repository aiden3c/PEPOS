import ui
import os
import pickle
import time

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

def init(buf, app, osData):
    print("running init")
    ui.draw_rectangle(buf, 0, 0, buf.width, buf.height, fill=255)
    app.variables["text_buffer"] = Buffer(buf.width, 10) #One line 10 tall to account for padding
    app.variables["cursor"] = (1, 1)
    app.variables["lastUpdate"] = time.time()
    osData["modules"].epdInitPartial(buf)
    return Command("setFlag", "noDraw", True)

def fix_char(text):
    if(text == "space"):
        return " "
    return text

def main(buf, inputs, app, osData):
    if osData["flags"]["keyboard"] and (len(osData["keyboardQueue"]) > 5 or time.time() - app.variables["lastUpdate"] > .5):
        print(app.variables["text_buffer"].width, app.variables["text_buffer"].height)
        for key in osData["keyboardQueue"]:
            key = fix_char(key)
            ui.draw_char(app.variables["text_buffer"], app.variables["cursor"][0], app.variables["cursor"][1], key)
            app.variables["cursor"] = (app.variables["cursor"][0] + 7, app.variables["cursor"][1])
            if app.variables["cursor"][0] > app.variables["text_buffer"].width - 7:
                tmp_text_buffer = Buffer(app.variables["text_buffer"].width, app.variables["text_buffer"].height + 10)
                #copy everything over
                for x in range(app.variables["text_buffer"].width):
                    for y in range(app.variables["text_buffer"].height):
                        tmp_text_buffer.buf[ x + y * tmp_text_buffer.width] = app.variables["text_buffer"].buf[x + y * app.variables["text_buffer"].width]
                app.variables["text_buffer"] = tmp_text_buffer
                app.variables["cursor"] = (1, app.variables["cursor"][1] + 10)
        osData["keyboardQueue"].clear()
        remaining = osData["modules"].epdDrawPartial(buf, app.variables["text_buffer"], 0, 0, app.variables["text_buffer"].width, app.variables["text_buffer"].height)
        app.variables["lastUpdate"] = time.time()
        if remaining == 0:
            #copy our text buffer to the main buffer
            for x in range(app.variables["text_buffer"].width):
                for y in range(app.variables["text_buffer"].height):
                    buf.buf[x + y * buf.width] = app.variables["text_buffer"].buf[x + y * app.variables["text_buffer"].width]
            osData["modules"].epdInitPartial(buf)
    osData["flags"]["keyboard"] = False #Acknowledge keyboard input
    return True

app = Application("terminal", init, main, nop, {"cursor": (0,0), "text": "", "text_buffer": Buffer(1, 1), "lastUpdate": time.time()})

