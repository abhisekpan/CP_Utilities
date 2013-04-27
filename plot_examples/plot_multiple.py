#! /usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111)
x = np.arange(0, 5, 0.1);
y = np.sin(x)
z = np.cos(x)
ax1.plot(x, y, x, z)
plt.show()
