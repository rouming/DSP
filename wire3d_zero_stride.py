"""
===================================
3D wireframe plots in one direction
===================================

Demonstrates that setting *rstride* or *cstride* to 0 causes wires to not be
generated in the corresponding direction.
"""

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np


fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(8, 12), subplot_kw={'projection': '3d'})

# Get the test data
X, Y, Z = axes3d.get_test_data(0.05)

#print(Y)

x = np.linspace(0, 100, 1000)
y = np.linspace(0, 100, 5)
X, Y = np.meshgrid(x, y)

Z = np.empty(shape=(0, len(x)))
for i in y:
    z = np.sin(x/10+i*10)
    Z = np.append(Z, [z], axis=0)

# Give the first plot only wireframes of the type y = c
ax1.plot_wireframe(X, Y, Z, cstride=0)
ax1.set_title("Column (x) stride set to 0")

# Give the second plot only wireframes of the type x = c
ax2.plot_wireframe(X, Y, Z, rstride=0)
ax2.set_title("Row (y) stride set to 0")

plt.tight_layout()
plt.show()
