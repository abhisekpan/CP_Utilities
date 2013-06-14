#!/usr/bin/env python
# a stacked bar plot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def plot_bar(width, *args):
    num_stacks = len(args) - 1
    ind = args[0]
    colors = ['r','y','b']
    labels = ['Men', 'Women', 'Dogs']
    ret_values = [None] * num_stacks
    op_file = PdfPages('stackedbar.pdf')
    fig = plt.figure()
    kwargs=dict()
    kwargs['linewidth'] = 0.1
    sp = fig.add_subplot(1, 1, 1)
    for i in xrange(1, num_stacks + 1):
        lower_stacks = np.sum([args[j] for j in xrange(1,i)], axis=0)
        print lower_stacks
        #ret_values[i - 1] 
        p = sp.bar(ind, args[i], width, color=colors[i-1], bottom=lower_stacks, **kwargs)
        print p
        p[0].set_label(labels[i-1])
        #p2 = plt.bar(ind, womenMeans, width, color='y', bottom=menMeans)
        #p3 = plt.bar(ind, dogMeans, width, color='b', bottom=humanMeans)

    #sp.set_position([0.1,0.1,0.9,0.9])
    plt.ylabel('Scores')
    plt.title('Scores by group and gender')
    plt.xticks(ind+width/2., ('G1', 'G2', 'G3', 'G4', 'G5') )
    plt.yticks(np.arange(0,100,10))
    plt.legend(loc=1)
    #sp.spines['left'].set_position(('data', 3.0))
    #sp.spines['bottom'].set_position(('data', 40))
    sp.spines['left'].set_position(('axes', 0.5))
    sp.spines['bottom'].set_position(('axes', 0.5))
    #sp.spines[direction].set_smart_bounds(True)
    for direction in ["right","top"]:
        sp.spines[direction].set_color('none')
    #plt.legend( (ret_values[0][0], ret_values[1][0], ret_values[2][0]), ('Men', 'Women', 'Dogs') )

    fig.savefig(op_file, format='PDF', dpi=80, bbox_inches='tight')
    op_file.close()
    plt.close(fig)
    #plt.show()

N = 5
menMeans = np.array([20, 35, 30, 35, 27])
womenMeans = np.array([25, 32, 34, 20, 25])
dogMeans = np.array([2, 3, 4, 5, 6])
ind_axis = np.arange(N)    # the x locations for the groups
data_list = [ind_axis, menMeans, womenMeans, dogMeans]
plot_bar(0.35, *data_list)

