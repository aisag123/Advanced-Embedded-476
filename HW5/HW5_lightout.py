import LCD
import time
import random
import GT911
from machine import Pin, I2C

LCD.Init()

WHITE = LCD.RGB(255, 255, 255)
BLACK = LCD.RGB(0, 0, 0)
YELLOW = LCD.RGB(255, 255, 0)

LCD.Clear(BLACK)

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
reset = Pin(10, Pin.OUT)
irq = Pin(11, Pin.IN)

touch = GT911.GT911(i2c, reset, irq)
touch.init()

round_ = 0
numbers = [8, 7, 6, 5, 4, 3, 2, 1, 0]

def generate_on_off():
    lights = []
    for i in range(9):
        lights.append(random.randint(0, 1))
    return lights

on_off = generate_on_off()

def draw_round():
    LCD.Solid_Box(20, 70, 150, 90, BLACK)
    LCD.Text("Round #: " + str(round_), 20, 75, WHITE, BLACK)

def draw_lights():
    LCD.Solid_Box(0, 90, 480, 210, BLACK)
    x = 10
    y = 100
    width = 50
    height = 100
    for i in range(9):
        LCD.Box(x, y, x + width, y + height, WHITE)
        if on_off[i] == 1:
            LCD.Solid_Box(x + 2, y + 2, x + width - 2, y + height - 2, YELLOW)
        LCD.Text(str(numbers[i]), x + 20, y + 105, WHITE, BLACK)
        x += 52

def toggle_light(position):
    on_off[position] ^= 1
    if position > 0:
        on_off[position - 1] ^= 1
    if position < 8:
        on_off[position + 1] ^= 1

def get_position(x_touch, y_touch):
    if y_touch < 100 or y_touch > 200:
        return -1
    for i in range(9):
        left = 10 + i * 52
        right = left + 50
        if left <= x_touch <= right:
            return i
    return -1

LCD.Text("Lights Out", 180, 20, WHITE, BLACK)
draw_round()
draw_lights()

was_touching = False

while True:
    number, points = touch.read_points()
    touching = number > 0

    if touching and not was_touching:
        x_touch = points[0][0]
        y_touch = points[0][1]
        position = get_position(x_touch, y_touch)
        print("Touch:", x_touch, y_touch, "-> position", position)

        if position != -1:
            toggle_light(position)
            round_ += 1
            draw_round()
            draw_lights()

            if sum(on_off) == 0:
                LCD.Text("You win!", 180, 45, YELLOW, BLACK)

    was_touching = touching
    time.sleep_ms(20)