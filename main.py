#!/usr/bin/python
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from signal import pause
import modules

from oslib import Buffer, Command, Application

width = modules.epd.width
height = modules.epd.height
buf = Buffer(width, height)

import ui
message = modules.motb+"\n\n"+modules.qotb
message_height = (len(ui.draw_page(buf, message, 1, 0, 0, noRender=True, returnLines=True)[1])) * 12
print("Bios write")
ui.draw_page(buf, message, 1, 0, 0, yoffset=buf.height-message_height, ignoreControls=True)
ui.draw_text(buf, 0, 0, "Loaded hardware interface.")
ui.draw_text(buf, 0, 10, "Initializing display: Done")
ui.draw_text(buf, 0, 20, "Loading applications:")
print("Bios commit")
modules.epdDraw(buf.buf)
try:
    import applications.apps as apps
    import applications.tester as tester
    import applications.terminal as terminal
except ImportError:
    ui.draw_text(buf, ui.text_bounds("Loading applications: ")[0], 20, "Failed")
    modules.epdDraw(buf.buf)
    ui.draw_text(buf, 0, 35, "This is where we'll load safe mode.")
    exit()
ui.draw_text(buf, ui.text_bounds("Loading applications: ")[0], 20, "Done")
ui.draw_text(buf, 0, 35, "Starting control system...")
modules.epdDraw(buf.buf)

def handleCommand(command):
    global buf
    global application
    global osData
    ret = command
    if ret.name == "launch": # application name
        print(f"Launching {ret.arguments[0]}")
        application.kill(application)
        application = mainApplications[ret.arguments[0]]
        initRet = application.init(buf, application, osData)
        if initRet != True:
            handleCommand(initRet)
        application.run(buf, [0, 0, 0, 0], application, osData)
    elif ret.name == "kill": # [no arguments]
        application.kill(application)
        application = launcher
        application.run(buf, [0, 0, 0, 0], application, osData)
    elif ret.name == "setFlag": # flag, val
        flag = ret.arguments[0]
        val  = ret.arguments[1]
        osData["flags"][flag] = val

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
    apps.tools,
    tester.testerApp,
    terminal.app,
]
mainApplications = {app.name: app for app in appList} #Access by name. This is the preferred method for app launching
launcher = mainApplications['launcher'] #Home option in main menu goes to this

#Control system variables/data init
application = launcher #Start with launcher
mainVariables = {
    'mainMenuOpened': False
}
osData = {
    'flags': {
        'keyboard': False,
        'shift': False,
        'backspace': False,
        'noDraw': False #Welcome to full hardware control, modules are your friend
    },
    'keyboardQueue': [],
    'modules': modules
}
mainMenu = ui.Menu(["Home"])
inputs = [0, 0, 0, 0]

def handleMain(inputs):
    #These need to be global, are modified from functions they're called in
    global application
    global buf
    global osData
    
    #emuInputs allows the control program to inject inputs into applications
    emuInputs = inputs
    if(inputs[3] == 1 and not osData['flags']['noDraw']):
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
                application.run(buf, emuInputs, application, osData)
            else:
                application.menuOptions[mainMenu.get_selected_option()](application)
                application.run(buf, emuInputs, application, osData)
    else:
        ret = application.run(buf, inputs, application, osData)
        if(ret is not True):
            handleCommand(ret)

    #Main menu overrides
    mainMenu.options = ["Home"]
    mainMenu.options.extend(application.menuOptions)

    #If application isn't taking over drawing, we draw our main menu, controls, and then commit te final buffer to the screen
    if not osData["flags"]["noDraw"]:
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
def handle_button1_press(_):
    inputs[0] = 1 
    input_pressed()
def handle_button2_press(_):
    inputs[1] = 1
    input_pressed()
def handle_button3_press(_):
    inputs[2] = 1
    input_pressed()
def handle_button4_press(_):
    inputs[3] = 1
    input_pressed() 
from pinpong.board import Board, Pin
btn4 = Pin(10, Pin.IN)
btn3 = Pin(11, Pin.IN)
btn2 = Pin(12, Pin.IN)
btn1 = Pin(13, Pin.IN)
_ = Pin(0, Pin.OUT) #Unused but fixes /sys/class/gpio. Blame pinpong, seriously

import time
last = [1, 1, 1, 1]
handleMain(inputs)
while True:
    if btn1.value() == 0 and last[0] == 1:
        handle_button1_press(None)
    if btn2.value() == 0 and last[1] == 1:
        handle_button2_press(None)
    if btn3.value() == 0 and last[2] == 1:
        handle_button3_press(None)
    if btn4.value() == 0 and last[3] == 1:
        handle_button4_press(None)
    last[0] = btn1.value()
    last[1] = btn2.value()
    last[2] = btn3.value()
    last[3] = btn4.value()
    time.sleep(0.05)

if (False):
    #Keyboard support
    def set_keyboard_flag():
        if(osData["flags"]["keyboard"] != True): #The running application must at least acknowledge this change by setting this to false after it runs. Refer to the Keyboard section of the documentation
            osData["flags"]["keyboard"] = True
            handleMain(inputs)

    import keyboard
    keyboard_timer = modules.Timer(1, set_keyboard_flag) #Unused for now, waiting on bugfix (TODO link bugfix lol)
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
        if(key.name == 'shift'):
            osData["flags"]["shift"] = True
            return
        if(key.name == 'backspace'):
            osData["flags"]["backspace"] = True
            return
        if(osData['flags']['shift']):
            osData["keyboardQueue"].append(key.name.upper())
        else:
            osData["keyboardQueue"].append(key.name)
        set_keyboard_flag()
    def handle_key_release(key):
        global osData
        if(key.name == 'shift'):
            osData["flags"]["shift"] = False
        if(key.name == 'backspace'):
            osData["flags"]["backspace"] = False

        if(key.name == 'ctrl'):
            set_keyboard_flag() #Temp to force update with no new characters until, again, previous bugfix
        
    keyboard.on_press(handle_keyboard_press)
    keyboard.on_release(handle_key_release)


handleMain(inputs)
pause()
