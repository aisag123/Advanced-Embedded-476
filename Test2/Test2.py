import LCD
from machine import Pin, I2C, Timer
from time import ticks_ms, ticks_diff
from gt911 import GT911

Black = LCD.RGB(0,0,0); Red = LCD.RGB(100,0,0)
Blue = LCD.RGB(0,0,100); White = LCD.RGB(100,100,100)
LCD.Init(); LCD.Clear(Black); LCD.Title('Over Under', White, Black)

touch = GT911(I2C(0, scl=Pin(9), sda=Pin(8), freq=100_000), Pin(10, Pin.OUT), Pin(11))
touch.init(touch_points=1, refresh_rate=50)

BAR_X1, BAR_X2, BAR_TOP, BAR_BOT = 200, 235, 100, 250
LAST_X, CUR_X, CARD_Y = 20, 100, 130
CARD_W, CARD_H = 45, 65
BTN_OVER  = (280, 60, 460, 120)
BTN_UNDER = (280, 135, 460, 195)
BTN_QUIT  = (280, 210, 460, 270)

bank = 100
pot = 0
deck = []
last_card = None
current_card = None
time_left = 100
state = "IDLE"
status = ""
cookie_taps = 0
cookie_on = False
shown_time = -1
touching = False
reset_flag = False
newgame_flag = False
last_press = 0

led = Pin(16, Pin.OUT)
btn_reset = Pin(14, Pin.IN, Pin.PULL_UP)
btn_new = Pin(15, Pin.IN, Pin.PULL_UP)

def debounced():
    global last_press
    now = ticks_ms()
    if ticks_diff(now, last_press) > 200:
        last_press = now
        return True
    return False

def isr_reset(p):
    global reset_flag
    if debounced():
        reset_flag = True

def isr_new(p):
    global newgame_flag
    if debounced():
        newgame_flag = True

btn_reset.irq(trigger=Pin.IRQ_FALLING, handler=isr_reset)
btn_new.irq(trigger=Pin.IRQ_FALLING, handler=isr_new)

def tick(t):
    global time_left
    if state == "PLAYING":
        time_left -= 1

timer = Timer(period=100, mode=Timer.PERIODIC, callback=tick)

def rank(c):
    return c % 13 + 1

def suit(c):
    return c // 13 + 1

def draw_card():
    global cookie_on
    if cookie_on:
        cookie_on = False
        led.value(0)
        for i in range(len(deck)):
            if rank(deck[i]) == 1:
                return deck.pop(i)
    return deck.pop()

def start_game():
    global bank, pot, deck, last_card, current_card
    global time_left, shown_time, cookie_taps, status, state
    bank -= 10
    pot = 1
    deck = LCD.Shuffle()
    last_card = None
    current_card = draw_card()
    time_left = 100
    shown_time = -1
    cookie_taps = 0
    status = ""
    state = "PLAYING"

def quit_game():
    global bank, pot, status, state
    bank += pot
    pot = 0
    status = "Cashed out"
    state = "IDLE"

def end_game(msg):
    global pot, status, state
    pot = 0
    status = msg
    state = "IDLE"

def bet(choice):
    global last_card, current_card, pot, time_left, shown_time
    last_card = current_card
    current_card = draw_card()
    old, new = rank(last_card), rank(current_card)
    if new != old:
        if (choice == "over") == (new > old):
            pot *= 2
        else:
            end_game("You lose")
            return
    time_left = 100
    shown_time = -1

def tap_card():
    global cookie_taps, cookie_on
    cookie_taps += 1
    if cookie_taps == 3:
        cookie_taps = 0
        cookie_on = True
        led.value(1)

def draw_button(box, label):
    LCD.Solid_Box(*box, Blue)
    LCD.Text2(label, box[0] + 20, box[1] + 15, White, Blue)

def draw():
    LCD.Solid_Box(20, 45, 190, 112, Black)
    LCD.Text2("bank: $" + str(bank), 20, 45, White, Black)
    LCD.Text2("pot: $" + str(pot), 20, 80, White, Black)

    LCD.Solid_Box(LAST_X, CARD_Y, LAST_X + CARD_W, CARD_Y + CARD_H, Black)
    LCD.Solid_Box(CUR_X, CARD_Y, CUR_X + CARD_W, CARD_Y + CARD_H, Black)
    if last_card is not None:
        LCD.Card(rank(last_card), suit(last_card), LAST_X, CARD_Y)
    if current_card is not None:
        LCD.Card(rank(current_card), suit(current_card), CUR_X, CARD_Y)
    LCD.Text("Last", LAST_X, CARD_Y + 70, White, Black)
    LCD.Text("Current", CUR_X, CARD_Y + 70, White, Black)

    draw_button(BTN_OVER, "Over")
    draw_button(BTN_UNDER, "Under")
    draw_button(BTN_QUIT, "Quit")

    LCD.Solid_Box(280, 280, 460, 312, Black)
    LCD.Text2(status, 280, 280, Red, Black)

def draw_timer():
    global shown_time
    t = max(time_left, 0)
    if t != shown_time:
        shown_time = t
        top = BAR_BOT - (BAR_BOT - BAR_TOP) * t // 100
        LCD.Solid_Box(BAR_X1, BAR_TOP, BAR_X2, top, Black)
        LCD.Solid_Box(BAR_X1, top, BAR_X2, BAR_BOT, White)

def inside(box, x, y):
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]

def handle_touch(x, y):
    if inside(BTN_OVER, x, y):
        bet("over")
    elif inside(BTN_UNDER, x, y):
        bet("under")
    elif inside(BTN_QUIT, x, y):
        quit_game()
    elif inside((CUR_X, CARD_Y, CUR_X + CARD_W, CARD_Y + CARD_H), x, y):
        tap_card()

draw()
while True:
    if reset_flag:
        reset_flag = False
        bank = 100
        draw()
    if newgame_flag:
        newgame_flag = False
        start_game()
        draw()

    n, pts = touch.read_points()
    if n == 0:
        touching = False
    elif not touching:
        touching = True
        if state == "PLAYING":
            handle_touch(pts[0][0], pts[0][1])
            draw()

    if state == "PLAYING":
        draw_timer()
        if time_left <= 0:
            end_game("Time's up")
            draw()