from machine import Pin, PWM, ADC
from time import sleep_ms

servo = PWM(Pin(2))
servo.freq(50)
joy = ADC(26)

a = 2.0 / 65535
b = 0.5

while True:
    ad = joy.read_u16()
    pw_ms = a * ad + b
    servo.duty_ns(int(pw_ms * 1_000_000))
    sleep_ms(20)