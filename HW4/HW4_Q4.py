from machine import Pin, ADC
from time import sleep_ms, ticks_ms, ticks_diff
import LCD

# ---------- Config ----------
PULSE_ADC_PIN = 26           # must be 26, 27, or 28 (GP number) for analog
DEBUG = False                # True: print raw ADC values to the REPL

# ---------- LCD setup ----------
LCD.Init()
Black = LCD.RGB(0, 0, 0)
White = LCD.RGB(250, 250, 250)
Grey = LCD.RGB(100, 100, 100)
Yellow = LCD.RGB(250, 250, 0)

def New_Screen():
    LCD.Clear(Black)
    LCD.Box(0, 0, 479, 319, White)
    LCD.Title('Pulse Sensor', White, Black)

Line_Black = bytearray(402)
Line_Grey = bytearray(402)
Line = bytearray(402)

for i in range(0, 201):
    Line_Grey[i*2] = Grey >> 8
    Line_Grey[i*2+1] = Grey & 0xFF

def Display(x, y):
    global Line, Line_Grey, Line_Black

    x += 1
    y = round(y)
    y = max(-100, min(100, y))

    LCD.Address_Set(x, 100, x, 300)
    LCD.StartWrite()
    LCD.dc.value(1)
    LCD.cs.value(0)

    if (x % 50) == 0:
        Line = Line_Grey
    else:
        Line = Line_Black

    ah = Line[200 - 2*y]
    al = Line[201 - 2*y]

    Line[200 - 2*y] = Yellow >> 8
    Line[201 - 2*y] = Yellow & 0xFF

    LCD.spi.write(Line)

    Line[200 - 2*y] = ah
    Line[201 - 2*y] = al

# ---------- Hardware ----------
pulse = ADC(PULSE_ADC_PIN)
buzzer = Pin(13, Pin.OUT)
led = Pin(16, Pin.OUT)

# ---------- BPM text ----------
def Show_BPM(bpm, ibi):
    # TODO: replace with your LCD module's text call (check print(dir(LCD)))
    LCD.Text(20, 40, "BPM: %3d   IBI: %4d ms   " % (bpm, ibi), White, Black)

# ---------- Beat detection settings ----------
SAMPLE_MS = 5                # sample period; plot every 2nd sample
MIN_IBI = 300                # ms (200 BPM max) hold-off
MAX_IBI = 2000               # ms (30 BPM min)
LED_MS = 100
BUZZ_MS = 5

smooth = pulse.read_u16()    # low-passed signal
base = smooth                # slow baseline (DC level)
amp = 500                    # tracked peak amplitude
armed = True                 # ready to detect next rising crossing

last_beat = ticks_ms()
led_t = 0
buzz_t = 0
ibis = []                    # recent beat intervals
bpm = 0
ibi = 0

New_Screen()
x = 0
n = 0

while True:
    now = ticks_ms()

    # --- read + filter ---
    raw = pulse.read_u16()
    if DEBUG:
        print(raw)
    smooth += (raw - smooth) * 0.3          # fast low-pass
    base += (smooth - base) * 0.01          # slow baseline
    d = smooth - base                       # AC component

    # amplitude tracking: rise fast, decay slowly
    if d > amp:
        amp = d
    else:
        amp -= amp * 0.002
    amp = max(amp, 300)                     # floor so noise isn't a "beat"
    thresh = amp * 0.5

    # --- beat detection ---
    if armed and d > thresh and ticks_diff(now, last_beat) > MIN_IBI:
        armed = False
        ibi = ticks_diff(now, last_beat)
        last_beat = now

        if ibi < MAX_IBI:
            ibis.append(ibi)
            if len(ibis) > 4:
                ibis.pop(0)
            avg = sum(ibis) / len(ibis)
            bpm = int(60000 / avg)
            Show_BPM(bpm, ibi)
        else:
            ibis = []                       # long gap: restart averaging

        led.value(1); led_t = now
        buzzer.value(1); buzz_t = now
    elif d < 0:
        armed = True                        # re-arm once signal falls back

    # --- non-blocking LED / buzzer off ---
    if led.value() and ticks_diff(now, led_t) >= LED_MS:
        led.value(0)
    if buzzer.value() and ticks_diff(now, buzz_t) >= BUZZ_MS:
        buzzer.value(0)

    # --- plot every 2nd sample (~10 ms per column) ---
    n += 1
    if n >= 2:
        n = 0
        Display(x, d / amp * 80)
        x += 1
        if x >= 478:
            x = 0

    sleep_ms(SAMPLE_MS)