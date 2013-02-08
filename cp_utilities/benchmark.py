'''
Created on Oct 28, 2011

@author: pana
'''
import figure as fig
import numpy as np
import sys

_capacities = ["64", "256", "512", "1K", "2K", "64K", "256K", "512K", "1M"]


class _ThreadData(object):
    pass


class Benchmark(object):
    '''Stores the data associated with a benchmark
    '''

    def __init__(self, name, num_threads):
        """Constructor"""
        self.name = name
        self.num_threads = num_threads
        self.thread_data = [_ThreadData() for dummy in xrange(self.num_threads)]
        for x in self.thread_data:
            x.miss_rate_all_intervals = dict() 
    def get_name(self):
        """ """
        return self.name
    
    def set_miss_rate_all_interval(self, thread, capacity, miss_rate_all_intervals):
        """ """
        assert(thread < self.num_threads)
        self.thread_data[thread].miss_rate_all_intervals[capacity] = miss_rate_all_intervals
        self.thread_data[thread].num_intervlals = len(miss_rate_all_intervals)
    
#    def get_num_intervals(self):
#        """ """
#        return 1

    def plot_mr_v_interval(self, new_style=False):
        """ Plot miss rate vs interval for all the threads """
        filename = self.name + "_mr_i.eps"
        subplots = len(_capacities)
        figure = fig.Figure(filename, title="Miss Rate vs Intervals",
                        num_subplots=subplots)

        for c in _capacities:
            plot_data = list()
            labels = list()
            for data in self.thread_data:
                intervals = np.arange(0, len(data.miss_rate_all_intervals[c]), 1)
                miss_rates = np.array(data.miss_rate_all_intervals[c])
                #label = "label=" + "Thread " + str(self.thread_data.index(data))
                plot_data.extend([intervals, miss_rates])
                labels.append('Thread ' + str(self.thread_data.index(data)))
            sp = figure.add_plot(new_style, labels, *plot_data)    
            figure.set_plot_param(sp, "intervals", "missrate", "Capacity: " + c)

        figure.save()
        figure.close()
    
    def read_from_file(self, bmfile):
        """ read benchmark related data from file"""
        IsThread = lambda line: line.startswith("thread")
        IsNumInterval = lambda line: line.startswith("num_intervals")
        IsMRAllIntervals = lambda line: line.startswith("miss_rate_all_intervals")
    
        # Initialization
        total_threads = 0
        sys.stderr.write("reading file " + bmfile + " for benchmark " + self.name + "\n")
        with open(bmfile, 'r') as src:
            for line in src:
                if IsThread(line):                
                    current_thrd = int(line.split(':', 1)[1])
                    total_threads += 1
                elif IsNumInterval(line):
                    num_intervals = int(line.split(':', 1)[1])
                        
                elif IsMRAllIntervals(line):
                    miss_rates_str = line.split(':', 1)[1].strip('[]\n')
                    miss_rates_list0 = miss_rates_str.split('], [')
                    miss_rates_list1 = [x.split(',') for x in miss_rates_list0]
                    assert(num_intervals == len(miss_rates_list1))
                    for cap in _capacities:
                        i = _capacities.index(cap)
                        miss_rates = [round(float(x[i]), 3) * 100.00
                                      for x in miss_rates_list1]
                        self.set_miss_rate_all_interval(current_thrd, cap, miss_rates)
                    
                else:
                    pass # not parsing for now    
               
            assert(total_threads == self.num_threads)
