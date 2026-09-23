from machine import Pin

test = Pin(15, Pin.OUT)

while(1):
    test.on()
