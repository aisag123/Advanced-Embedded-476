from machine import Pin, UART
from neopixel import NeoPixel
from time import sleep_ms, ticks_ms, ticks_diff

import LCD

UTC_OFFSET = -6
KNOTS_TO_MPH = 1.15078
MEASURE_MS = 10000

LCD.Init()
Black = LCD.RGB(0, 0, 0)
White = LCD.RGB(250, 250, 250)
Yellow = LCD.RGB(250, 250, 0)
Green = LCD.RGB(0, 250, 0)
Red = LCD.RGB(250, 0, 0)

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), rxbuf=1024)

NUM_PIXELS = 8
np = NeoPixel(Pin(9), NUM_PIXELS)

PIXEL = [(0, 0, 40), (40, 0, 0), (40, 15, 0)]
OFF = (0, 0, 0)

hh = mm = ss = 0
speed = 0.0
fix = False
have_time = False
top3 = []
state = "IDLE"
max_speed = 0.0
start_ms = 0
start_flag = False
buf = b''

def btn_irq(pin):
    global start_flag
    start_flag = True

btn = Pin(15, Pin.IN, Pin.PULL_UP)
btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_irq)

def touch_pressed():
    return False

def parse_line(line):
    global hh, mm, ss, speed, fix, have_time
    try:
        s = line.decode('ascii').strip()
    except UnicodeError:
        return
    if s[3:6] != 'RMC':
        return
    f = s.split(',')
    if len(f) < 8:
        return
    try:
        if f[2] == 'A' and len(f[1]) >= 6:
            hh, mm, ss = int(f[1][0:2]), int(f[1][2:4]), int(f[1][4:6])
            speed = float(f[7]) * KNOTS_TO_MPH if f[7] else 0.0
            fix = True
            have_time = True
        else:
            fix = False
    except ValueError:
        pass

def poll_gps():
    global buf
    n = uart.any()
    if not n:
        return
    buf += uart.read(n)
    while b'\n' in buf:
        line, buf = buf.split(b'\n', 1)
        parse_line(line)
    if len(buf) > 300:
        buf = b''

def New_Screen():
    LCD.Clear(Black)
    LCD.Box(0, 0, 479, 319, White)
    LCD.Title('How Fast Can I Run?', White, Black)
    LCD.Text("Time:", 20, 50, White, Black)
    LCD.Text("Speed:", 20, 90, White, Black)
    LCD.Text("Top 3 Speeds", 20, 170, White, Black)
    LCD.Text("1st", 20, 210, Yellow, Black)
    LCD.Text("2nd", 20, 250, Yellow, Black)
    LCD.Text("3rd", 20, 290, Yellow, Black)

shown = {}

def put(slot, text, x, y, color):
    if shown.get(slot) != text:
        LCD.Text(text, x, y, color, Black)
        shown[slot] = text

def draw_all():
    if have_time:
        h = (hh + UTC_OFFSET) % 24
        t = "%d:%02d:%02d %s" % (h % 12 or 12, mm, ss, "PM" if h >= 12 else "AM")
    else:
        t = "--:--:--"
    put("time", "%-12s" % t, 120, 50, White)
    put("speed", "%-10s" % ("%.1f mph" % speed if fix else "-- mph"), 120, 90, White)

    if state == "MEASURING":
        left = max(0, MEASURE_MS - ticks_diff(ticks_ms(), start_ms)) // 1000 + 1
        put("status", "%-20s" % ("MEASURING %ds" % left), 20, 130, Green)
    elif fix:
        put("status", "%-20s" % "Ready - press GP15", 20, 130, White)
    else:
        put("status", "%-20s" % "Waiting for GPS fix", 20, 130, Red)

    for i in range(3):
        v = "%.1f mph" % top3[i] if i < len(top3) else "--"
        put("top%d" % i, "%-10s" % v, 120, 210 + 40 * i, White)

def record(v):
    global top3
    place = 0
    while place < len(top3) and top3[place] >= v:
        place += 1
    if place < 3:
        top3.insert(place, v)
        top3 = top3[:3]
    return place

def fill(color):
    for i in range(NUM_PIXELS):
        np[i] = color
    np.write()

def set_pixel(place):
    fill(PIXEL[place] if place < 3 else OFF)

def begin():
    global state, max_speed, start_ms, start_flag
    state = "MEASURING"
    max_speed = speed
    start_ms = ticks_ms()
    start_flag = False
    fill(OFF)

def finish():
    global state
    state = "IDLE"
    set_pixel(record(max_speed))

fill(OFF)
New_Screen()

try:
    while True:
        poll_gps()

        if state == "IDLE":
            if (start_flag or touch_pressed()) and fix:
                begin()
            start_flag = False
        else:
            start_flag = False
            if fix and speed > max_speed:
                max_speed = speed
            if ticks_diff(ticks_ms(), start_ms) >= MEASURE_MS:
                finish()

        draw_all()
        sleep_ms(20)

finally:
    fill(OFF)