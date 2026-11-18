from machine import Pin, ADC, Timer
from time import sleep_ms, ticks_ms, ticks_diff

import LCD

PULSE_ADC_PIN = 26
BUZZER_ACTIVE_LOW = False

MIN_AMP = 1000
PLOT_FLOOR = 2000
SMOOTH_K = 0.09
MIN_IBI = 400
MAX_IBI = 2000
WARMUP_MS = 2000
NO_BEAT_MS = 3000
LED_MS = 100
BUZZ_MS = 40

LCD.Init()
Black = LCD.RGB(0, 0, 0)
White = LCD.RGB(250, 250, 250)
Grey = LCD.RGB(100, 100, 100)
Yellow = LCD.RGB(250, 250, 0)

Line_Black = bytearray(402)
Line_Grey = bytearray(402)
Line = bytearray(402)

for i in range(0, 201):
    Line_Grey[i*2] = Grey >> 8
    Line_Grey[i*2+1] = Grey & 0xFF

def New_Screen():
    LCD.Clear(Black)
    LCD.Box(0, 0, 479, 319, White)
    LCD.Title('Pulse Sensor', White, Black)
    LCD.Text("BPM:", 20, 40, White, Black)
    LCD.Text("IBI:", 180, 40, White, Black)
    LCD.Text("ms", 268, 40, White, Black)

def Display(x, y):
    global Line
    x += 1
    y = max(-100, min(100, round(y)))

    LCD.Address_Set(x, 100, x, 300)
    LCD.StartWrite()
    LCD.dc.value(1)
    LCD.cs.value(0)

    Line = Line_Grey if (x % 50) == 0 else Line_Black

    ah = Line[200 - 2*y]
    al = Line[201 - 2*y]
    Line[200 - 2*y] = Yellow >> 8
    Line[201 - 2*y] = Yellow & 0xFF
    LCD.spi.write(Line)
    Line[200 - 2*y] = ah
    Line[201 - 2*y] = al

def Show_BPM(bpm, ibi):
    LCD.Number(bpm, 3, 0, 60, 40, White, Black)
    LCD.Number(ibi, 4, 0, 220, 40, White, Black)

pulse = ADC(PULSE_ADC_PIN)
buzzer = Pin(13, Pin.OUT)
led = Pin(16, Pin.OUT)

BUZZ_ON = 0 if BUZZER_ACTIVE_LOW else 1
BUZZ_OFF = 1 - BUZZ_ON

def read_pulse():
    total = 0
    for _ in range(16):
        total += pulse.read_u16()
    return total >> 4

def beat_feedback(now):
    led.value(1)
    buzzer.value(BUZZ_ON)
    Timer(period=LED_MS, mode=Timer.ONE_SHOT, callback=lambda t: led.value(0))
    Timer(period=BUZZ_MS, mode=Timer.ONE_SHOT, callback=lambda t: buzzer.value(BUZZ_OFF))
    
buzzer.value(BUZZ_OFF)
led.value(0)

smooth = read_pulse()
base = smooth
amp = MIN_AMP
armed = True
start = ticks_ms()
last_beat = None
led_t = 0
buzz_t = 0
ibis = []
bpm = 0
x = 0
n = 0

New_Screen()
Show_BPM(0, 0)

try:
    while True:
        now = ticks_ms()

        smooth += (read_pulse() - smooth) * SMOOTH_K
        base += (smooth - base) * 0.005
        d = smooth - base

        if d > amp:
            amp = d
        else:
            amp -= amp * 0.002
        amp = max(amp, MIN_AMP)

        if armed and d > amp * 0.6 and ticks_diff(now, start) > WARMUP_MS:
            armed = False
            if last_beat is None:
                last_beat = now
                beat_feedback(now)
            else:
                ibi = ticks_diff(now, last_beat)
                if ibi >= MIN_IBI:
                    last_beat = now
                    if ibi <= MAX_IBI:
                        ibis.append(ibi)
                        if len(ibis) > 4:
                            ibis.pop(0)
                        bpm = int(60000 / (sum(ibis) / len(ibis)))
                        Show_BPM(bpm, ibi)
                    else:
                        ibis = []
                    beat_feedback(now)
        elif d < 0:
            armed = True

        if bpm and ticks_diff(now, last_beat) > NO_BEAT_MS:
            bpm = 0
            ibis = []
            last_beat = None
            Show_BPM(0, 0)

        n += 1
        if n >= 2:
            n = 0
            Display(x, d / max(amp, PLOT_FLOOR) * 80)
            x = (x + 1) % 478

        sleep_ms(5)

finally:
    buzzer.value(BUZZ_OFF)
    led.value(0)