inputs = [0, 0, 0, 0]
def input_pressed():
    global inputs
    print(inputs)
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
Board('MILKV-DUO').begin()
btn1 = Pin(10, Pin.IN)
btn2 = Pin(11, Pin.IN)
btn3 = Pin(12, Pin.IN)
btn4 = Pin(13, Pin.IN)
_ = Pin(0, Pin.OUT) #Unused but fixes /sys/class/gpio. Blame pinpong, seriously

import time
last = [1, 1, 1, 1]
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