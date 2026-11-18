from machine import Pin
from neopixel import NeoPixel

np = NeoPixel(Pin(9), 8)
for i in range(8):
    np[i] = (0, 0, 40)
np.write()