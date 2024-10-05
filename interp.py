#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

def lin_interp(y1, y2, mu):
    return y1*(1-mu)+y2*mu

def cos_interp(y1, y2, mu):
   mu2 = (1 - np.cos(mu*np.pi))/2
   return y1*(1-mu2)+y2*mu2

def cubic_interp(y0, y1, y2, y3, mu):
   mu2 = mu*mu
   a0 = y3 - y2 - y0 + y1
   a1 = y0 - y1 - a0
   a2 = y2 - y0
   a3 = y1
   return a0*mu*mu2+a1*mu2+a2*mu+a3

f = 4
t = np.linspace(0, 1, 100, endpoint=False)

sine = np.sin(2*np.pi*t * f)

t_each5 = t[::5]
sine_each5 = sine[::5]

n_points = len(t)
n_seg = len(t_each5) - 1


# Except last point
n_points_per_seg = (n_points - 1) // n_seg
n_points_extra = (n_points - 1) - int(n_points_per_seg * n_seg)

sine_inter = np.array([])
for i_seg in range(0, n_seg):
    n = n_points_per_seg
    #if n_points_extra > 0:
        #n_points_extra -= 1
        #n += 1

    mu = 1 / n

    p0 = sine_each5[i_seg]
    p1 = sine_each5[i_seg + 1]

    if i_seg == 0:
        p_beg = p0
    else:
        p_beg = sine_each5[i_seg - 1]

    if i_seg + 1 == n_seg:
        p_end = p1
    else:
        p_end = sine_each5[i_seg + 1]

    sine_inter = np.append(sine_inter, p0)
    for i_p in range(0, n - 1):
        mu = 1 / n * (i_p + 1)
        p = cos_interp(p0, p1, mu)
        #p = cubic_interp(p_beg, p0, p1, p_end, mu)

        sine_inter = np.append(sine_inter, p)

    if i_seg + 1 == n_seg:
        sine_inter = np.append(sine_inter, p1)

plt.plot(t, sine)
plt.plot(t_each5, sine_each5, 'x')
if n_points_extra:
    plt.plot(t[:-n_points_extra], sine_inter, '-')
else:
    plt.plot(t, sine_inter, '-')
plt.show()
