from time import sleep
from pitop import Button, LED, UltrasonicSensor, Buzzer
from pitop import Pitop
from pitop.miniscreen import Miniscreen
import datetime
import pyttsx3

# Green LED in port D4
gled = LED("D4")
# Red LED
rled = LED("D5")
# Button on port D2
button = Button("D2")
# Ultrasonic Sensor on port D6
sensor = UltrasonicSensor("D6")
# Buzzer on port D3
buzzer = Buzzer("D3")
# pi-top miniscreen
miniscreen = Miniscreen()
# Initialize pyttsx3
tts = pyttsx3.init()

button.hold_time = 3 # Button hold time required to activate panic feature
sensor.threshold_distance = 0.39 # Sensor distance required to activate alarm when armed

# Initial states of variables
active = False
panic = False
exitdelay = True

# Initial system state is disarmed, turn on green LED and report status in console
gled.on()
print("Alarm off")

# Enable/disable exit delay, triggered by X button
def exit_timer_toggle():
    global exitdelay
    if exitdelay == False:
        exitdelay = True
        print("Exit delay on")
    else:
        exitdelay = False
        print("Exit delay off")

# Restart the exit timer, triggered by O button on pi-top
def restartexit():
    global active
    if not active:
        print("You can't restart the exit delay, the alarm is not on")
    elif active and not exitdelay:
        print("You can't restart the exit delay, the exit delay is disabled")
    elif active:
        active = False
        rled.blink(0.5, 0.5)
        gled.blink(0.5, 0.5)
        buzzer.blink(0.1,1)
        for i in range(15,0,-1):
            print(str.format("You have {} seconds to exit", i))
            sleep(1)
        active = True
        rled.on()
        gled.off()
        buzzer.off()
        print("Alarm on")

# Main alarm trigger function
def alarm():
    global active
    if active:
        #buzzer.on()
        buzzer.blink(0.1, 0.1, 10)
        rled.blink(0.1, 0.1)
        print("ALARM TRIGGERED at", datetime.datetime.now())
        tts.say("Alarm triggered")
        tts.runAndWait()

# Panic alarm, triggered by holding main button
def panic():
    global active
    global panic
    panic = True
    active = True
    gled.off()
    rled.blink(0.1, 0.1)
    #buzzer.on()
    buzzer.blink(0.1, 0.1)
    print("PANIC")
    tts.say("Panic alarm activated")
    tts.runAndWait()

# Main system toggle function, triggered by main button
def systemtoggle():
    global active
    global panic
    if not active and exitdelay:
        tts.say("Alarm active in 15 seconds")
        tts.runAndWait()
        rled.blink(0.5, 0.5)
        gled.blink(0.5, 0.5)
        buzzer.blink(0.1,1)
        for i in range(15,0,-1):
            print(str.format("You have {} seconds to exit", i))
            sleep(1)
        active = True
        rled.on()
        gled.off()
        buzzer.off()
        print("Alarm on")
        tts.say("System armed")
        tts.runAndWait()
    elif not active:
        active = True
        rled.on()
        gled.off()
        buzzer.off()
        print("Alarm on")
        tts.say("System armed")
        tts.runAndWait()
    elif active == True and panic == False:
        active = False
        buzzer.off()
        rled.off()
        gled.on()
        print("Alarm off")
        tts.say("System disarmed")
        tts.runAndWait()
    else:
        panic = False
button.when_released = systemtoggle
button.when_held = panic
miniscreen.cancel_button.when_released = exit_timer_toggle
miniscreen.select_button.when_released = restartexit
sensor.when_in_range = alarm