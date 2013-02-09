"""
Exports the Benchmark class, which is responsible for storing and plotting the
data corresponding to a benchmark.
"""
import figure as fig
import numpy as np
import sys


_cache_capacities = ["64", "256", "512", "1K", "2K", "64K", "256K", "512K", "1M"]


class _ThreadData(object):
    """ Holds per-thread data.

    Acts as a structure so-to-speak, stores all data per thread.
    Members:
    miss_rate_all_intervals: dictionary, the keys are cache capacities, and
    the value is a list of miss-rates for all intervals for that capacity.
    rd_profiles: dictionary, keys are intervals and value is a dictionary of
    frequencies for different bins of reuse-distance ie. bins are keys and
    frequencies are values.
    """
    pass


class Benchmark(object):
    """Stores the data associated with a benchmark"""

    def __init__(self, name, num_threads):
        """Constructor"""
        self.name = name
        self.num_threads = num_threads
        self.__thread_data = [_ThreadData() for dummy in xrange(self.num_threads)]
        for thread_data in self.__thread_data:
            thread_data.miss_rate_all_intervals = dict()
            thread_data.rd_profiles = dict()

    def set_rd_profile(self, thread, interval, rd_profile):
        """Store the list of reuse-distance frequencies for an interval for a
        thread.
        """
        self.__thread_data[str(thread)].rd_profiles[interval] = rd_profile
    
    def plot_rd_profiles(self, new_style=False):
        """Plot reuse-distance profile for all intervals for all threads.
        
        A separate file for each thread. Each subplot is for an interval.
        X-axis denotes the number of reuse-distance bins and Y-axis denotes the
        frequency of accesses.
        """
        for data in self.__thread_data:
            plot_id = str(self.__thread_data.index(data))
            filename = self.name + "_t" + plot_id + "_rdp.eps"
            subplots = len(data.rd_profiles)
            figure = fig.Figure(filename, 
                                title="RD Profile for thread " + plot_id,
                                num_subplots=subplots)
            #labels = list()
            for num_interval in data.rd_profiles:
                bins_list = list()
                freq_list = list()
                for dist, freq in data.rd_profiles[num_intervals].iteritems():
                    bins_list.append(dist)
                    freq_list.append(freq)
                bins = np.array(bins_list)
                rd_freq = np.array(freq_list)
                #label = "label=" + "Thread " + str(self.__thread_data.index(data))
                plot_data = [bins, rd_freq]
                #labels.append('Thread ' + str(self.__thread_data.index(data)))
                labels = ['Interval: ' + num_interval]
                sp = figure.add_plot(new_style, labels, *plot_data)    
                figure.set_plot_param(sp, "reuse distance", "frequency",
                                      "Interval: " + num_interval)

            figure.save()
            figure.close()

    def read_rddata_from_file(self, bmfile):
        """Read reuse distance profile data from file."""
        IsInterval = lambda line: line.startswith("Interval")
        IsThread = lambda line: line.startswith("thread")
        IsHistogram = lambda line: line.startswith("histogram")
    
        # Initialization
        current_interval = 0
        current_thrd = 0

        with open(bmfile, 'r') as src:
            for line in src:
                if IsInterval(line):
                    current_interval = current_interval + 1
                
                elif IsThread(line):
                    current_thrd = int(line.split(':', 1)[1])

                elif IsHistogram(line):
                    rd_profile = dict()
                    histo_line = line[11:-2]
                    token_list = histo_line.split()
                    for token in token_list:
                        token.rstrip(',')
                        distance = token.split(':')[0]
                        frequency = token.rstrip(',').split(':')[1]
                        rd_profile[dist] = frequency
                    
                    set_rd_profile(current_thread, current_interval,
                                   rd_profile)
                else:
                    pass  # other cases are not relevant

    def set_miss_rate_all_interval(self, thread, cache_capacity,
                                   miss_rate_all_intervals):
        """Store the list of miss-rates for all intervals for a cache
        capacity for a thread
        """
        self.__thread_data[thread].miss_rate_all_intervals[cache_capacity] = \
                miss_rate_all_intervals
    
    def plot_mr_v_interval(self, new_style=False):
        """ Plot miss rate vs interval for all the threads.
        
        Each subplot is for a particular cache capacity. X-axis denotes the
        number of intervals and Y-axis denotes the miss-rate. All threads are
        plotted in one sub-plot.
        """
        filename = self.name + "_mr_i.eps"
        subplots = len(_cache_capacities)
        figure = fig.Figure(filename, title="Miss Rate vs Intervals",
                        num_subplots=subplots)

        for c in _cache_capacities:
            plot_data = list()
            labels = list()
            for data in self.__thread_data:
                intervals = np.arange(0, len(data.miss_rate_all_intervals[c]), 1)
                miss_rates = np.array(data.miss_rate_all_intervals[c])
                #label = "label=" + "Thread " + str(self.__thread_data.index(data))
                plot_data.extend([intervals, miss_rates])
                labels.append('Thread ' + str(self.__thread_data.index(data)))
            sp = figure.add_plot(new_style, labels, *plot_data)    
            figure.set_plot_param(sp, "intervals", "missrate", "Capacity: " + c)

        figure.save()
        figure.close()
    
    def read_mrdata_from_file(self, bmfile):
        """Read miss-rate vs interval data from file."""
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
                    for cap in _cache_capacities:
                        i = _cache_capacities.index(cap)
                        miss_rates = [round(float(x[i]), 3) * 100.00
                                      for x in miss_rates_list1]
                        self.set_miss_rate_all_interval(current_thrd, cap, miss_rates)
                    
                else:
                    pass # not parsing for now    
               
            assert(total_threads == self.num_threads)
