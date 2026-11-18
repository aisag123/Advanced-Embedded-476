import matplotlib.pyplot as plt

files = ["temp_run1.txt", "temp_run2.txt", "temp_run3.txt"]

for name in files:
    t, temp = [], []
    with open(name) as f:
        next(f)
        for line in f:
            a, b = line.strip().split(",")
            t.append(float(a))
            temp.append(float(b))
    plt.plot(t, temp, marker="o", markersize=3, label=name)

plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("DS18B20 temperature vs. time")
plt.grid(True)
plt.legend()
plt.show()