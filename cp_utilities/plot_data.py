'''
Created on Oct 28, 2011

@author: pana
'''
import figure as fig
import numpy as np

def plot_mr_v_interval(benchmarks, filename, same_axis=True):
    """ Plot miss rate vs interval for benchmarks. """
    if same_axis: 
        subplots = 1
        new_style = True
    else:   
        subplots = len(benchmarks)
        new_style = False
    figure = fig.Figure(filename, title="Miss Rate vs Intervals",
                        num_subplots=subplots)
    for bm in benchmarks:
        bm.plot_mr_v_interval(figure, new_style)
        
    figure.save()
    figure.close()

if __name__ == '__main__':
    pass
