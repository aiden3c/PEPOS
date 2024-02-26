#!/usr/bin/python

#BIOS START
print("Booting PEPOS...")
import sys
import os
import pickle
print("Importing driver...", end="\r")
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from signal import pause
import modules
from oslib import Buffer, Command, Application, OSSetting, save_pickle, load_pickle

width = modules.display.epd.width
height = modules.display.epd.height
buf = Buffer(width, height)

#Able to draw BIOS on hardware
import ui
message = modules.motb+"\n\n"+modules.qotb
message_height = (len(ui.draw_page(buf, message, 1, 0, 0, noRender=True, returnLines=True)[1])) * 12
ui.draw_page(buf, message, 1, 0, 0, yoffset=buf.height-message_height, ignoreControls=True)
ui.draw_text(buf, 0, 0, "Loaded hardware interface.")
ui.draw_text(buf, 0, 10, "Initializing display: Done")
ui.draw_text(buf, 0, 20, "Loading applications:")
print("EPD tradeoff. See you later!")
modules.epdInitPartial(modules.display, buf)
try:
    import applications.apps as apps
    sys.modules['apps'] = apps
    import applications.tester as tester
    import applications.terminal as terminal
    import applications.newdrawtest as drawtest
    import applications.settings as settings
    import vnovel.main as catquest
except ImportError:
    ui.draw_text(buf, 0, 20, "Loading applications: Fail")
    ui.draw_text(buf, 0, 35, "Starting safe mode...")
    exit()
ui.draw_text(buf, 0, 20, "Loading applications: Done")
ui.draw_text(buf, 0, 35, "Starting control system...")
modules.display.epd.display_Partial(buf.buf, buf.update.x, buf.update.y, buf.update.x2, buf.update.y2)
#BIOS done

def handleCommand(command):
    #The application context being global is important, I think the others can be passed through
    global buf
    global application
    global osData
    ret = command
    #"command": # arguments
    if ret.name == "launch": # application name
        print(f"Launching {ret.arguments[0]}")
        ui.draw_rectangle(buf, 8, (height // 2) - 16, width - 8, (height // 2) + 16, 0)
        ui.draw_rectangle(buf, 10, (height // 2) - 14, width - 10, (height // 2) + 14)
        text_size = ui.text_bounds(f"Starting {ret.arguments[0]}...")
        ui.draw_text(buf, (width // 2) - (text_size[0] // 2), (height // 2) - (text_size[1] // 2), f"Starting {ret.arguments[0]}...")
        modules.epdDrawAny(modules.display, buf)
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
    drawtest.app,
    settings.app,
    catquest.app
]
mainApplications = {app.name: app for app in appList} #Access by name. This is the preferred method for app launching
launcher = mainApplications['launcher'] #Home option in main menu goes to this

#Control system variables/data init
application = launcher #Start with launcher
if(not os.path.exists("osSettings.pkl")):
    osSettings = {setting.name: setting for setting in [
        OSSetting("inputDelay", .1, scale=.1),
        OSSetting("statusLED", True)
    ]}
    save_pickle("osSettings.pkl", osSettings)
else:
    osSettings = load_pickle("osSettings.pkl")

mainVariables = {
    'mainMenuOpened': False
}
osData = {
    'flags': {
        'keyboard': False,
        'shift': False,
        'backspace': False,
        'noDraw': False, #Full drawing control, modules are your friend
    },
    'keyboardQueue': [],
    'modules': modules, #For passthrough to applications
    'booting': True,
    'settings': osSettings
}
mainMenu = ui.Menu(["Home"])
inputs = [0, 0, 0, 0]

def statusOn():
    if(osSettings['statusLED']):
        led.value(1)

def statusOff():
    if(osSettings['statusLED']):
        led.value(0)

def handleMain(inputs):
    #These need to be global, are modified from functions they're called in
    global application
    global buf
    global osData
    
    #emuInputs allows the control program to inject inputs into applications
    emuInputs = inputs
    if(inputs[3] == 1 and not osData['flags']['noDraw']):
        mainVariables['mainMenuOpened'] = not mainVariables['mainMenuOpened']
        if(mainVariables['mainMenuOpened'] and modules.display.mode != "partial"):
            statusOn()
            modules.epdInitPartial(modules.display, buf)
            statusOff()       


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
                initRet = application.init(buf, application, osData)
                if initRet != True:
                    handleCommand(initRet)
            else:
                application.menuOptions[mainMenu.get_selected_option()](application)
            ret = application.run(buf, emuInputs, application, osData)
            if(ret is not True):
                handleCommand(ret)

    else:
        ret = application.run(buf, inputs, application, osData)
        if(ret is not True):
            handleCommand(ret)

    mainMenu.options = ["Home"]
    mainMenu.options.extend(application.menuOptions)

    #If application isn't taking over drawing, we draw our main menu, controls, and then commit te final buffer to the screen
    if not osData["flags"]["noDraw"]:
        statusOn()
        if(mainVariables['mainMenuOpened']):
            buf.clearUpdate()
            mainMenu.draw(buf, (width // 3), 0, width, len(mainMenu.options)*16, size=1)
        if modules.display.mode == "fast": #or ((buf.update.x2 - buf.update.x) * (buf.update.y2 - buf.update.y)) / (buf.width * buf.height) > 0.55: #If we're updating over 50% of the screen, just do a normal draw
            drawControls()
            modules.epdDraw(modules.display, buf)
        else:
            remaining = modules.epdDrawPartial(modules.display, buf, buf.update.x, buf.update.y, buf.update.x2, buf.update.y2)
            print(f"{remaining} partial calls left")
        statusOff()

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
led = Pin(25, Pin.OUT)

import time
last = [1, 1, 1, 1]

application.init(buf, application, osData)
osData['booting'] = False
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
    time.sleep(osSettings['inputDelay'].value) #More sleep means less power. 0.10 is about 2.6-3.3%

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
