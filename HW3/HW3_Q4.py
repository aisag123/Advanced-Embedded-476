from machine import Pin
from time import sleep

password = "0123"
guess = ""
incorrect = 0

Beeper = Pin(13, Pin.OUT)
Button_clear = Pin(14, Pin.IN, Pin.PULL_UP)
Button = Pin(15, Pin.IN, Pin.PULL_UP)
unlock_led = Pin(16, Pin.OUT)
incorrect_led = Pin(17, Pin.OUT)

button_1 = Pin(2, Pin.IN, Pin.PULL_UP)
button_2 = Pin(3, Pin.IN, Pin.PULL_UP)
button_3 = Pin(4, Pin.IN, Pin.PULL_UP)
button_4 = Pin(5, Pin.IN, Pin.PULL_UP)

def unlock():
    global guess
    unlock_led.on()
    sleep(1)
    unlock_led.off()
    guess = ""

def denied():
    global incorrect, guess
    incorrect += 1
    incorrect_led.on()
    sleep(1)
    incorrect_led.off()
    guess = ""

    if incorrect == 3:
        Beeper.value(1)
        sleep(1)
        Beeper.value(0)
        incorrect = 0

def checkCombo(pin_str):
    pin = pin_str if pin_str != "" else 0
    print("guessed", pin_str)
    if pin == password:
        unlock()
        print("unlocked")
    else:
        denied()
        print("denied")

def on_button_click(digit):
    global guess
    if len(guess) < 4:
        guess = guess + str(digit)
    return guess

def readPin():
    global guess
    if button_1.value() == 0:
        on_button_click(0)
        sleep(0.2)
    elif button_2.value() == 0:
        on_button_click(1)
        sleep(0.2)
    elif button_3.value() == 0:
        on_button_click(2)
        sleep(0.2)
    elif button_4.value() == 0:
        on_button_click(3)
        sleep(0.2)

    if Button.value() == 0:
        checkCombo(guess)
        sleep(0.2)
    elif Button_clear.value() == 0:
        guess = ""
        print(guess)
        sleep(0.3)

while(1):
    readPin()