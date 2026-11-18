from time import sleep_ms, ticks_ms, ticks_diff, sleep
import LCD
from machine import Pin 
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import random

#want to send a start command like pass 10 - place 6 10  - auto roll after bet is rec
#place bets on number 6 and 8

LCD.Init()
Black = LCD.RGB(0, 0, 0)
White = LCD.RGB(250, 250, 250)

BANK = 100.0

start_flag = False
ON_FLAG = False
OFF_FLAG = True

ble = bluetooth.BLE()
sp = BLESimplePeripheral(ble)

LED0 = Pin("LED", Pin.OUT)

def on_rx(data):
    global BANK
    global OFF_FLAG
    print("Data received: ", data)
    parts = data.decode().strip().upper().split(',')
    if OFF_FLAG == True:
        if parts[0] == 'PASS':
            print("pass bet")
            #new game - take money from bank
            try:
                bet = int(parts[1])
            except ValueError:
                print('invalid bet')
                return
            if bet <= 0 or bet > BANK:
                print('invalid bet')
                return
            print('Bank: ', BANK)
            print('Bet: ', bet)
            BANK -= bet
            print('Bank after bet: ', BANK)
            result = roll()
            print('roll: ', result)
            #this calls the handle roll win/loss logic
        else:
            print('invalid: use (pass, #)')
    elif data == b'place':
        print('place bet')

def btn_irq(pin):
    global start_flag
    start_flag = True
    roll()

btn = Pin(15, Pin.IN, Pin.PULL_UP)
btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_irq)

def New_Screen():
    LCD.Clear(Black)
    LCD.Box(0, 0, 479, 319, White)
    LCD.Title('Craps', White, Black)
    LCD.Text("Bank:", 20, 60, White, Black)
    LCD.Text("Phase:", 20, 120, White, Black)
    LCD.Text("Point", 20, 180, White, Black)
    LCD.Text("Roll", 20, 240, White, Black)

def roll():
    first_die = random.randint(1, 6)
    second_die = random.randint(1, 6)
    return first_die + second_die

def pass_handler():
    ...
    
def place_handler():
    ...

New_Screen()

while(1):
    if sp.is_connected():
        sp.on_write(on_rx)