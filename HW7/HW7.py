import LCD
import random
from math import sqrt
from machine import Pin, Timer
from time import ticks_ms, ticks_diff

LCD.Init()

BLACK = LCD.RGB(0, 0, 0)
WHITE = LCD.RGB(255, 255, 255)
LCD.Clear(BLACK)

BUZZ_MS   = 5
BEATS_OUT = 5
BEATS_IN  = 10

buzzer    = Pin(13, Pin.OUT)
btn_click = Pin(15, Pin.IN, Pin.PULL_UP)
btn_new   = Pin(14, Pin.IN, Pin.PULL_UP)

beat_timer = Timer()
off_timer  = Timer()

bpm = 0
period_f = 0.0
t0 = 0
beats_out = 0
beats = 0
err = 0.0
mean = 0.0
std_dev = 0.0
sum_err = 0.0
sum_sq = 0.0

click_flag = 0
click_time = 0
last_click = 0
new_flag = 1
last_new = 0

def buzz_off(t):
    buzzer.value(0)

def beat_isr(t):
    global beats_out
    buzzer.value(1)
    off_timer.init(mode=Timer.ONE_SHOT, period=BUZZ_MS, callback=buzz_off)
    beats_out += 1
    if beats_out >= BEATS_OUT:
        beat_timer.deinit()

def click_isr(pin):
    global click_flag, click_time, last_click
    now = ticks_ms()
    if ticks_diff(now, last_click) < 50:
        return
    last_click = now
    if beats_out >= BEATS_OUT and beats < BEATS_IN and not click_flag:
        click_time = now
        click_flag = 1

def new_isr(pin):
    global new_flag, last_new
    now = ticks_ms()
    if ticks_diff(now, last_new) < 50:
        return
    last_new = now
    new_flag = 1

btn_click.irq(trigger=Pin.IRQ_FALLING, handler=click_isr)
btn_new.irq(trigger=Pin.IRQ_FALLING, handler=new_isr)

def draw_text(x, y, text):
    LCD.Text(text, x, y, WHITE, BLACK)

def show_status():
    LCD.Solid_Box(0, 0, 479, 250, BLACK)
    draw_text(20, 10,  "Drummer Trainer")
    draw_text(20, 50,  "BPM: " + str(bpm))
    draw_text(20, 90,  "# Beats: " + str(beats))
    draw_text(20, 130, "Error: {:.0f} ms".format(err))
    draw_text(20, 170, "Mean: {:.1f} ms".format(mean))
    draw_text(20, 210, "St Dev: {:.1f} ms".format(std_dev))

def start_game():
    global bpm, period_f, t0, beats_out, beats, err, mean, std_dev
    global sum_err, sum_sq, click_flag
    beat_timer.deinit()
    off_timer.deinit()
    buzzer.value(0)

    bpm = random.randint(40, 80)
    period_f = 60000 / bpm
    beats_out = 0
    beats = 0
    err = mean = std_dev = 0.0
    sum_err = sum_sq = 0.0
    click_flag = 0
    show_status()

    t0 = ticks_ms()
    beat_isr(None)
    beat_timer.init(mode=Timer.PERIODIC, period=round(period_f), callback=beat_isr)


def process_click():
    """Compute error and running stats for one user beat."""
    global beats, err, mean, std_dev, sum_err, sum_sq, click_flag
    expected = (BEATS_OUT + beats) * period_f
    actual = ticks_diff(click_time, t0)
    err = actual - expected

    beats += 1
    sum_err += err
    sum_sq += err * err
    mean = sum_err / beats
    var = sum_sq / beats - mean * mean
    std_dev = sqrt(var) if var > 0 else 0.0

    click_flag = 0
    show_status()


while True:
    if new_flag:
        new_flag = 0
        start_game()
    if click_flag:
        process_click()