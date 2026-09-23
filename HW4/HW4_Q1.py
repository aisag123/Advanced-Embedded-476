from machine import Pin, ADC
from time import sleep

x = ADC(26)
y = ADC(27)

while(1):
    print(x.read_u16(), y.read_u16())
    sleep(0.1)