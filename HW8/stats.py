import numpy as np
from scipy.optimize import curve_fit

def model(t, y0, x, a):
    return y0 + (x - y0) * (1 - np.exp(-t / a))

data = np.loadtxt("temp_run3.txt", delimiter=",", skiprows=1)
t, temp = data[:, 0], data[:, 1]

popt, _ = curve_fit(model, t, temp, p0=[temp[0], temp[-1], 10])
print("y0 = %.2f  x = %.2f  a = %.2f s" % tuple(popt))