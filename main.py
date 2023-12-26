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
import ui
import apps

class Buffer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buf = [0xFF] * (int(width/8) * height)

width = modules.epd.width
height = modules.epd.height

inputs = [0, 0, 0, 0]

logging.basicConfig(level=logging.DEBUG)

buf = Buffer(width, height)

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


appList = [
    apps.launcher,
    apps.reader,
    apps.tools
]
launcher = appList[0]
mainApplications = {app.name: app for app in appList}

application = launcher

mainVariables = {
    'mainMenuOpened': False
}

buf_width = width
buf_height = height
buf = Buffer(buf_width, buf_height)
mainMenu = ui.Menu(["Home"])
def drawMain(inputs):
    global application
    global buf
    
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
            else:
                application.menuOptions[mainMenu.get_selected_option()](application)
                application.run(buf, emuInputs, application)

    else:
        ret = application.run(buf, emuInputs, application)
        if(ret is not True): #Make this a command if its not true, instead of a code to assume application switching
            print(f"Swapping application to {ret}")
            application.kill(application)
            application = mainApplications[ret]
            application.run(buf, [0, 0, 0, 0], application)

    #Application overrides
    mainMenu.options = ["Home"]
    mainMenu.options.extend(application.menuOptions)

    if(mainVariables['mainMenuOpened']):
        mainMenu.draw(buf, (width // 3), 0, width, height)

    drawControls()

    modules.epdDraw(buf.buf)

def input_pressed():
    global inputs
    drawMain(inputs)
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

drawMain(inputs)
pause()