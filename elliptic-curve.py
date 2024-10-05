#!/usr/bin/python3

import random
import time
import re

# E: y^2 = x^3 + 2x + 2 (mod 17)
G_arr = [(5, 1), (6, 3)]
a = 2
n = 19

# S = (3Xg^2 + a) / 2Yg
# X2 = S^2 - 2Xg
# Y2 = S(Xg - X2) - Yg
def point_2x(G):
    #                                 Modular multiplicative inverse (mod 17)
    s = (((3 * G[0]**2 + a) % 17) * pow(2 * G[1], -1, 17)) % 17
    x = (s**2 - 2 * G[0]) % 17
    y = (s * (G[0] - x) - G[1]) % 17
    return (x, y)

# S = (Yp - Yq) / (Xp - Xq)
# Xr = S^2 - (Xp + Xq)
# Yr = S(Xp - Xr) - Yp
def point_add(P, Q):
    #                   Modular multiplicative inverse (mod 17)
    Py_min_Qy = P[0] - Q[0]
    if Py_min_Qy == 0:
        return None
    s = ((P[1] - Q[1]) * pow(Py_min_Qy, -1, 17)) % 17
    x = (s**2 - (P[0] + Q[0])) % 17
    y = (s * (P[0] - x) - P[1]) % 17
    return (x, y)


# Generate points
P = G_arr[1]
for i in range(3, n):
    P = point_add(G_arr[0], P)
    G_arr.append(P)


random.seed(time.time())
secret = random.randrange(1, n-1)
P = G_arr[secret]


print("Your public P=(%u,%u)" % (P[0], P[1]))
string = input("Enter peer public P: ")
pair = re.match('(\d+),(\d+)', string)
peer_P = (int(pair.group(1)), int(pair.group(2)))

P = peer_P
for i in range(0, secret):
    Pn = point_add(P, G_arr[0])
    if Pn is None:
        Pn = point_add(P, G_arr[1])
    P = Pn

print("Secret: (%u,%u)" % (P[0], P[1]))
