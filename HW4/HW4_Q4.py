from machine import Pin, PWM, ADC
from time import sleep, ticks_ms

servo = PWM(Pin(2))
servo.freq(50)
a2d0 = ADC(26)

dt = 0.01
y = 0

kx = 100 / 65535

while True:
    x = kx * a2d0.read_u16()
    dy = -y + x
    y += dy * dt

    pw_ms = 0.5 + 2.0 * (y / 100)
    servo.duty_ns(int(pw_ms * 1_000_000))

    print(ticks_ms(), x, y, pw_ms)
    sleep(dt)