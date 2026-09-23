from machine import Pin, PWM
from time import sleep

servo = PWM(Pin(2))
servo.freq(50)

def set_pulse_ms(ms):
    servo.duty_ns(int(ms * 1_000_000))

for ms in (0.5, 1.5, 2.5):
    set_pulse_ms(ms)
    sleep(1)