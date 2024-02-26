import ui
import os

from oslib import Application, Buffer, Command, OSSetting, nop, pickle, save_pickle, load_bitmap

def adjust_setting(setting: OSSetting, inputs):
    print(setting.type)

def init(buf, app, osData):
    ui.draw_rectangle(buf, 0, 0, buf.width, buf.height, fill=255)
    osData['modules'].display.mode = "fast"
    osData['modules'].epdDraw(osData['modules'].display, buf)
    location = os.path.dirname(__file__)+os.path.sep
    image = location+"foxkeh.bmp"
    bmp = load_bitmap(image, buf.width, buf.height, inv=True)
    i=0
    for pixel in bmp:
        char = " "
        if(pixel):
            char = "@"
        if i == buf.width:
            print()
            i = 0
        print(char, end="")
        i += 1
    return True

def kill(app):
    return True

def main(buf, inputs, app, osData):
    ui.draw_text(buf, 5, 5, "Game started")
    return True

app = Application("catquest", init, main, kill, {})
