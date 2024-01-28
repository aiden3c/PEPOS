import ui
import os
import pickle

from oslib import Application, Buffer, Command, BufferUpdate

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

def init(buf, app, osData): #We use nop instead of init in this example
    ui.draw_rectangle(buf, 0, 0, buf.width, buf.height, fill=255)
    app.variables["updateBuffer"] = Buffer(buf.width, buf.height)
    osData["modules"].epdInitPartial(buf)
    return Command("setFlag", "noDraw", True)

def kill(buf, inputs, app, osData): #We do use this function as our kill though, even though it doesn't do anything. To show you can do both.
    return True

#This doesn't work, instead have the updatebuffer as a variable. we also need accurate buffer update setting with text/char drawing
def main(buf: Buffer, inputs: list[bool], app: Application, osData):
    if inputs[0]:
        ui.draw_text(app.variables["updateBuffer"], 5, 5, "Hello world!")
        ui.draw_text(app.variables["updateBuffer"], 5, 16, "Expanded")
        
        #How long until a full refresh is forced
        if osData["modules"].epdDrawPartial(buf, app.variables["updateBuffer"], app.variables["updateBuffer"].update.x, app.variables["updateBuffer"].update.y, app.variables["updateBuffer"].update.x+app.variables["updateBuffer"].update.x2, app.variables["updateBuffer"].update.y+app.variables["updateBuffer"].update.y2) == 0:
            for x in range(app.variables["updateBuffer"].width):
                for y in range(app.variables["updateBuffer"].height):
                    buf.buf[x + y * buf.width] = app.variables["updateBuffer"].buf[x + y * app.variables["updateBuffer"].width]
            osData["modules"].epdInitPartial(buf)

    return True

app = Application("drawtest", init, main, kill, {"buttonMsg": "Button!"})
