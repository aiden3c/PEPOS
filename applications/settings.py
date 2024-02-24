import ui
import os

from oslib import Application, Buffer, Command, OSSetting, nop, pickle, save_pickle

def adjust_setting(setting: OSSetting, inputs):
    print(setting.type)

def init(buf, app, osData):
    ui.draw_rectangle(buf, 0, 0, buf.width, buf.height)
    osData['modules'].display.mode = "fast"
    osData['modules'].epdDraw(osData['modules'].display, buf)
    osData['modules'].display.mode = "partial"

    app.variables["menu"] = ui.Menu([setting in osData['settings']])
    return True

def kill(app):
    save_pickle("osSettings.pkl", osData['settings'])
    return True

def main(buf, inputs, app, osData):
    ui.draw_text(buf, 5, 5, "Hello world!")
    if inputs[0] == 1:
        ui.draw_text(buf, 5, 15, app.variables["buttonMsg"])
    return True

app = Application("settings", init, main, kill, {"buttonMsg": "Button!"})
