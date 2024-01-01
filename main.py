#!/usr/bin/python
import logging
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from signal import pause
import modules
class Buffer:
    def __init__(self, width, height, data = 0xFF):
        self.width = width
        self.height = height
        self.buf = [data] * (int(width/8) * height)
width = modules.epd.width
height = modules.epd.height
buf = Buffer(width, height)

import ui

message = modules.motb+"\n\n"+modules.qotb
message_height = (len(ui.draw_page(buf, message, 1, 0, 0, noRender=True, returnLines=True)[1])) * 12
ui.draw_page(buf, message, 1, 0, 0, yoffset=buf.height-message_height, ignoreControls=True)

ui.draw_text(buf, 0, 0, "Loaded hardware interface.")
ui.draw_text(buf, 0, 10, "Initializing display: Done")
ui.draw_text(buf, 0, 20, "Loading applications:")
modules.epdDraw(buf.buf, True)
import apps
ui.draw_text(buf, ui.text_bounds("Loading applications: ")[0], 20, "Done")
ui.draw_text(buf, 0, 35, "Starting control system...")
modules.epdDraw(buf.buf, True)


inputs = [0, 0, 0, 0]

#Draw the controls at the bottom of the screen, accounting for text length.
def drawControls(text = ['Up', 'Select', 'Down']):
    ui.draw_rectangle(buf, 0, height - 20, width, height, fill=255)
    ui.draw_line(buf, 10, height - 18, width - 10, height - 18)
    ui.draw_text(buf, 8, height - 12, text[0])
    ui.draw_text(buf, width // 2 - 30, height - 12, text[1])
    ui.draw_text(buf, width - 50, height - 12, text[2])
    menuChar = '-'
    if(mainVariables['mainMenuOpened']):
        menuChar = 'O'
    ui.draw_text(buf, width - 10, height - 12, menuChar)

#Used for main menu app switching
appList = [
    apps.launcher, #Application launcher/home menu
    apps.reader,
    apps.tools
]
mainApplications = {app.name: app for app in appList} #Access by name. This is the preferred method
launcher = mainApplications['launcher'] #Home option in main menu goes to this

application = launcher #Start with launcher
mainVariables = {
    'mainMenuOpened': False
}
osData = {
    'flags': {
        'keyboard': False
    },
    'keyboardQueue': []
}
mainMenu = ui.Menu(["Home"])
def handleMain(inputs):
    #These need to be global, are modified from functions they're called in
    global application
    global buf
    global osData
    
    #emuInputs allows the control program to inject inputs into applications
    emuInputs = inputs
    if(inputs[3] == 1):
        mainVariables['mainMenuOpened'] = not mainVariables['mainMenuOpened']

    if(mainVariables['mainMenuOpened']):
        emuInputs = [0, 0, 0, 0] #Dont pass inputs to application
        if(inputs[0] == 1):
            mainMenu.select_previous()
        if(inputs[2] == 1):
            mainMenu.select_next()
        if(inputs[1] == 1):
            val = mainMenu.selection
            mainVariables['mainMenuOpened'] = False
            if(val == 0):
                application.kill(application)
                application = launcher
                application.run(buf, [0, 0, 0, 0], application, osData)
            else:
                application.menuOptions[mainMenu.get_selected_option()](application)
                application.run(buf, emuInputs, application, osData)
    else:
        ret = application.run(buf, inputs, application, osData)
        if(ret is not True): #Make this a command if its not true, instead of a code to assume application switching
            print(f"Swapping application to {ret}")
            application.kill(application)
            application = mainApplications[ret]
            application.run(buf, [0, 0, 0, 0], application, osData)

    #Main menu overrides
    mainMenu.options = ["Home"]
    mainMenu.options.extend(application.menuOptions)

    #After application is ran/drawn (or not), we render the main menu, controls ui, and finally commit the final buffer to the screen
    if(mainVariables['mainMenuOpened']):
        mainMenu.draw(buf, (width // 3), 0, width, height, size=1)

    drawControls()

    modules.epdDraw(buf.buf)

#One main call per input
def input_pressed():
    global inputs
    handleMain(inputs)
    inputs = [0, 0, 0, 0]

#Callbacks
def handle_button1_press():
    inputs[0] = 1 
    input_pressed()
def handle_button2_press():
    inputs[1] = 1
    input_pressed()
def handle_button3_press():
    inputs[2] = 1
    input_pressed()
def handle_button4_press():
    inputs[3] = 1
    input_pressed() 
callbacks = {
    1: handle_button1_press,
    2: handle_button2_press,
    3: handle_button3_press,
    4: handle_button4_press,
}
input = modules.Input({1: modules.btn1, 2: modules.btn2, 3: modules.btn3, 4: modules.btn4})
input.on_button_press(callbacks)

def set_keyboard_flag():
    if(osData["flags"]["keyboard"] != True):
        osData["flags"]["keyboard"] = True
        handleMain(inputs)
import keyboard
keyboard_timer = modules.Timer(1, set_keyboard_flag)
def handle_keyboard_press(key):
    global osData
    global keyboard_timer
    if(key.name == 'up'):
        handle_button1_press()
        return
    if(key.name == 'down'):
        handle_button3_press()
        return
    if(key.name == 'left'):
        handle_button2_press()
        return
    if(key.name == 'right'):
        handle_button4_press()
        return
    keyboard_timer.start()
    osData["keyboardQueue"].append(key.name)
    if(len(osData["keyboardQueue"]) > 5):
        set_keyboard_flag()

handleMain(inputs)
pause()
