import machine, onewire, ds18x20, time, os
from machine import Pin

ds_pin = machine.Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
button = machine.Pin(15, Pin.IN, Pin.PULL_UP)

roms = ds_sensor.scan()
print('Found DS devices: ', roms)

def next_filename():
    existing = os.listdir()
    n = 1
    while "temp_run%d.txt" % n in existing:
        n += 1
    return "temp_run%d.txt" % n

def collect():
    fname = next_filename()
    print("Logging to", fname)
    with open(fname, "w") as f:
        f.write("time_s,temp_c\n")
        start = time.ticks_ms()
        for i in range(60):
            ds_sensor.convert_temp()
            time.sleep_ms(750)
            temp = ds_sensor.read_temp(roms[0])
            f.write("%d,%.2f\n" % (i, temp))
            f.flush()
            print(i, temp)
            next_t = time.ticks_add(start, (i + 1) * 1000)
            time.sleep_ms(max(0, time.ticks_diff(next_t, time.ticks_ms())))
    print("Done:", fname)

def read_temp():
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        print(rom)
        print(ds_sensor.read_temp(rom))
    time.sleep(5)

print("Press GP15 to start")
while True:
    if button.value() == 0:
        time.sleep_ms(30)
        if button.value() == 0:
            collect()
            while button.value() == 0:
                time.sleep_ms(10)
            print("Press GP15 to start")
    time.sleep_ms(10)