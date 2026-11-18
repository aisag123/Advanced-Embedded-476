import LCD
import random
from machine import Pin
from time import ticks_ms, ticks_diff

LCD.Init()

BLACK = LCD.RGB(0, 0, 0)
WHITE = LCD.RGB(255, 255, 255)
RED   = LCD.RGB(255, 0, 0)
BLUE  = LCD.RGB(0, 0, 255)
LCD.Clear(BLACK)

btn_jump = Pin(15, Pin.IN, Pin.PULL_UP)
btn_new  = Pin(14, Pin.IN, Pin.PULL_UP)

jump_flag = 0
jump_time = 0
new_flag  = 0
last_jump = 0
last_new  = 0

def jump_isr(pin):
    global jump_flag, jump_time, last_jump
    now = ticks_ms()
    if ticks_diff(now, last_jump) < 50:
        return
    last_jump = now
    if not jump_flag:
        jump_time = now
        jump_flag = 1

def new_isr(pin):
    global new_flag, last_new
    now = ticks_ms()
    if ticks_diff(now, last_new) < 50:
        return
    last_new = now
    new_flag = 1

btn_jump.irq(trigger=Pin.IRQ_FALLING, handler=jump_isr)
btn_new.irq(trigger=Pin.IRQ_FALLING, handler=new_isr)

jump_num = 0
score = 0
T = 1000
t_mid = 500
start = 0
old_x = 0
jumped = False

Y_TOP, Y_BOT, Y_LINE = 140, 260, 200

def draw_text(x, y, text):
    LCD.Text(text, x, y, WHITE, BLACK)
    
def show_status():
    LCD.Solid_Box(0, 0, 479, 100, BLACK)
    draw_text(20, 20, "Jump #" + str(jump_num))
    draw_text(20, 60, "Score = " + str(score))

def draw_marker():
    LCD.Solid_Box(240, Y_TOP, 243, Y_BOT, BLUE)

def draw_rope(x):
    global old_x
    if x == old_x:
        return
    LCD.Solid_Box(x, Y_TOP, x + 3, Y_BOT, RED)
    LCD.Solid_Box(old_x, Y_TOP, x - 1, Y_BOT, BLACK)
    LCD.Solid_Box(old_x, Y_LINE, x + 3, Y_LINE + 1, WHITE)
    old_x = x
    draw_marker()

def clear_field():
    LCD.Solid_Box(0, Y_TOP, 479, Y_BOT, BLACK)
    LCD.Solid_Box(0, Y_LINE, 479, Y_LINE + 1, WHITE)
    draw_marker()

def new_round():
    global T, t_mid, start, old_x, jumped, jump_flag
    T = random.randint(500, 1500)
    t_mid = T * 240 // 479
    jumped = False
    jump_flag = 0
    old_x = 0
    clear_field()
    print("T =", T, "t_mid =", t_mid)
    start = ticks_ms()

def fail():
    global jump_num, score
    jump_num = 0
    score = 0
    print("too late - game over")
    show_status()
    new_round()

def score_jump(jump_ms):
    global jump_num, score, jumped
    jumped = True
    if jump_ms < t_mid:
        early = t_mid - jump_ms
        pts = max(0, 100 - early)
        jump_num += 1
        score += pts
        print("jumped", early, "ms early ->", pts, "pts")
        show_status()
    else:
        fail()

show_status()
new_round()

while True:
    if new_flag:
        new_flag = 0
        jump_num = 0
        score = 0
        show_status()
        new_round()

    elapsed = ticks_diff(ticks_ms(), start)

    if elapsed >= T:
        new_round()
        continue

    draw_rope(elapsed * 479 // T)

    if not jumped:
        if jump_flag:
            score_jump(ticks_diff(jump_time, start))
        elif elapsed >= t_mid:
            fail()