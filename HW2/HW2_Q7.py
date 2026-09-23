from machine import Pin
from time import sleep

motor_in1 = Pin(14, Pin.OUT)
motor_in2 = Pin(15, Pin.OUT)

while True:
    # Clockwise
    motor_in1.on()
    motor_in2.off()
    sleep(1)
    
    # Stop
    motor_in1.off()
    motor_in2.off()
    sleep(1)
    
    # Counter-clockwise
    motor_in1.off()
    motor_in2.on()
    sleep(1)
    
    # Stop
    motor_in1.off()
    motor_in2.off()
    sleep(1)