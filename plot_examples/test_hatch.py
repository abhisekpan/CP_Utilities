#! /usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

filename = PdfPages('test_hatch' + '.' + 'pdf')
plot_params = {'backend': 'PDF'}
plt.rcParams.update(plot_params)
fig = plt.figure()
patterns = [ "/" , "\\" , "|" , "-" , "+" , "x", "o", "O", ".", "*" ]
ind = np.array([1,2,3,4,5])
dep1 = np.array([10,20,40,80,160])
dep2 = np.array([50,50,50,50,50])
dep3 = np.array([5,5,5,5,5])
dep4 = np.array([75,75,75,75,75])
markers = ['*', 'o', '^','+']
ax1 = fig.add_subplot(111)
#for i in range(len(patterns)):
    #ax1.bar(i, 3, color='red', edgecolor='black', hatch=patterns[i])
#ax1.plot(ind, dep1, 'ko', ind, dep2, 'k*', ind, dep3, 'ks', ind, dep4, 'k^', markersize=8.0)
lines = ax1.plot(ind, dep1, ind, dep2, ind, dep3, ind, dep4, color='k', linestyle='', markersize=8.0)
i = 0
print lines
for line in lines:
    print line
    line.set_marker(markers[i])
    i+=1
fig.savefig(filename, format='PDF', dpi=150, bbox_inches='tight')
filename.close()
plt.show()
