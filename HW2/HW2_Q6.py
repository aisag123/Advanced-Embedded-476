from machine import Pin
from time import sleep

on_board_1 = Pin(16, Pin.OUT)
on_board_2 = Pin(17, Pin.OUT)
red_led = Pin(18, Pin.OUT)

while True:
    on_board_1.on()
    sleep(1)
    on_board_1.off()
    
    on_board_2.on()
    sleep(1)
    on_board_2.off()
    
    red_led.on()
    sleep(1)
    red_led.off()
