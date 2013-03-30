"""
Exports the Benchmark class, which is responsible for storing and plotting the
data corresponding to a benchmark. Utility class that is used by most scripts.
"""
import datetime as dt
import figure as fig
import numpy as np
import sys


_cache_capacities = ["64", "256", "512", "1K", "2K", "64K", "256K", "512K", "1M"]
_MAGIC_MISS_DISTANCE = 4611686018427387904.0  #2^62

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

    def __init__(self, name, num_threads, num_sets=1, num_ways=1):
        """Constructor"""
        self.name = name
        self.num_threads = num_threads
        self.num_sets = num_sets
        self.num_ways = num_ways
        assert (num_ways % num_threads == 0), \
            "Number of ways should be multiple of number of threads"
        self.capacities = [x * num_sets for x in xrange(1, num_ways + 1)]
        self.capacities.append(int(_MAGIC_MISS_DISTANCE))  # infinite capacity
        #print "cap: ", self.capacities
        self.__thread_data = [_ThreadData() for 
            dummy in xrange(self.num_threads)]
        for thread_data in self.__thread_data:
            thread_data.miss_rate_all_intervals = dict()
            thread_data.rd_profiles = dict()
            thread_data.freq_v_cap = dict()
    
    def set_rd_profile(self, thread, profile_id, rd_profile):
        """Store the list of reuse-distance frequencies for an id for a
        thread.
        """
        self.__thread_data[thread].rd_profiles[profile_id] = rd_profile
    
    def set_freq_cdf(self, thread, profile_id, freq_cdf):
        """Store the cdf for frequencies with capacities for an id for a
        thread.
        """
        self.__thread_data[thread].freq_v_cap[profile_id] = freq_cdf
    
    def get_freq_cdf(self, thread, profile_id):
        """Return the cdf for frequencies with capacities for an id for a
        thread.
        """
        return self.__thread_data[thread].freq_v_cap[profile_id]
    
    def plot_rd_profiles(self, new_style=False, filter_distance=0.0,
                         file_suffix=None):
        """Plot reuse-distance profile for all ids for all threads.
        
        A separate file for each thread. Each subplot is for an interval.
        X-axis denotes the number of reuse-distance bins and Y-axis denotes the
        frequency of accesses.
        Filter_distance is used to simulate the effects of a smaller filtering
        cache (such as the filtering effects of an L1 cache for an L2 cache).
        Filter_distance is equal to the capacity of the filtering cache. We
        assume that all accesses with distance <  the filter_distance will be
        hit. Of course this does not take into account of the effect filtering
        has on the distance values of the references which pass through the
        filter, which can increase, decrease, or stay the same depending on
        the sequence of references.
        """
        for data in self.__thread_data:
            plot_id = str(self.__thread_data.index(data))
            if not(file_suffix):
                file_suffix = dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
            filename = self.name + "/" + self.name + "_t" + plot_id + "_rdp" + file_suffix
            subplots = len(data.rd_profiles)
            #if subplots > 50: subplots = 50
            print "subplot: ", subplots
            subplots_per_page = subplots if subplots < 2 else 2
            figure = fig.Figure(filename,
                                figformat='pdf',
                                title="RD Profile for thread " + plot_id,
                                total_subplots=subplots,
                                subplots_per_page=subplots_per_page,
                                font_size=3)
            for profile_id in data.rd_profiles:
                print "profile id: ", profile_id
                # Sort the rd_profile on distance
                # Distances in string, but sort on their values
                sorted_bins =  data.rd_profiles[profile_id].keys()
                sorted_bins.sort(key=lambda x:float(x))
                bins_list = list()
                freq_list = list()
                x_index = 0
                for dist in sorted_bins:
                    if float(dist) < filter_distance:
                        continue
                    bins_list.append(x_index)
                    x_index = x_index + 1
                    freq_list.append(int(data.rd_profiles[profile_id][dist]))
                bins = np.array(bins_list)
                rd_freq = np.array(freq_list)
                plot_data = [bins, rd_freq]
                if (filter_distance > 0):
                    dist_labels = [x for x in sorted_bins 
                        if float(x) >= filter_distance]
                else:
                    dist_labels = sorted_bins
                legend_labels = ['Profile Id ' + str(profile_id)]
                sp = figure.add_plot(new_style, legend_labels, 'reuse distance',
                                     'frequency', 
                                     'Profile Id ' + str(profile_id), dist_labels,
                                     *plot_data)    
                if profile_id >= subplots:
                    break

            figure.save_and_close()

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
                        token = token.rstrip(',')
                        distance = '%.2f' %float(token.split(':')[0])
                        frequency = token.split(':')[1]
                        if float(distance) < _MAGIC_MISS_DISTANCE:
                            rd_profile[distance] = frequency
                    self.set_rd_profile(current_thrd, current_interval,
                                        rd_profile)
                else:
                    pass  # other cases are not relevant

    def build_freq_vs_capacity_profile(self):
        """For each thread & interval build cdf of freq vs capacity."""
        for t, tdata in enumerate(self.__thread_data):
            for profile_id, rd_profile in tdata.rd_profiles.iteritems():
                freq_cdf = [0 for dummy in xrange(len(self.capacities))]
                running_total = running_idx = 0
                sorted_keys = sorted(rd_profile.iterkeys(), key=lambda x: float(x))
                for dist in sorted_keys:
                    freq = rd_profile[dist]
                    while (float(dist) >= self.capacities[running_idx]):
                        freq_cdf[running_idx] = running_total
                        running_idx += 1
                    running_total += int(freq)
                while running_idx < len(self.capacities):
                    freq_cdf[running_idx] = running_total
                    running_idx += 1
                self.set_freq_cdf(t, profile_id, freq_cdf)

    def find_best_partition(self):
        """For each interval for each thread as preferred thread, find the
        best possible partition"""
        default_alloc = self.num_ways / self.num_threads
        max_alloc = self.num_ways - (self.num_threads - 1)
        num_profiles = len(self.__thread_data[0].freq_v_cap)
        best_allocations = list()
        for preferred_t in xrange(self.num_threads):
            sys.stdout.write("Preferred thread: %d\n" % preferred_t)
            best_allocations_per_thread = list()
            for profile_id in xrange(num_profiles):
                max_gain = 0
                best_alloc = default_alloc
                preferred_alloc = default_alloc + (self.num_threads - 1)
                other_alloc = default_alloc - 1
                while (preferred_alloc <= max_alloc):
                    pos_gain = self.gain(preferred_t, profile_id + 1, 
                                         default_alloc, preferred_alloc)
                    neg_gain = sum(self.gain(t, profile_id + 1,
                                   default_alloc, other_alloc)
                        for t in xrange(self.num_threads) if t != preferred_t)
                    gain = pos_gain + neg_gain
                    if gain > max_gain:
                        max_gain = gain
                        best_alloc = preferred_alloc
                    preferred_alloc += (self.num_threads - 1)
                    other_alloc -= 1
                best_allocations_per_thread.append(best_alloc)
                sys.stdout.write("Best Alloc for Interval %d: %d\n" % 
                    (profile_id + 1, best_alloc))
            best_allocations.append(best_allocations_per_thread)
        return best_allocations

    def gain(self, thread, profile_id, from_alloc, to_alloc):
        "Return the gain obtained between two allocations"""
        g = (self.__thread_data[thread].freq_v_cap[profile_id][to_alloc - 1] -
            self.__thread_data[thread].freq_v_cap[profile_id][from_alloc - 1])
        return g

    def read_cluster_rddata_from_file(self, bmfile):
        """Read cluster reuse distance profile data from file."""
        IsCluster = lambda line: line.startswith("cluster")
        IsThread = lambda line: line.startswith("thread")
        IsHistogram = lambda line: line.startswith("histogram_eqn")
    
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
                        token = token.rstrip(',')
                        distance = '%.2f' %float(token.split(':')[0])
                        frequency = token.split(':')[1]
                        if float(distance) < _MAGIC_MISS_DISTANCE:
                            rd_profile[distance] = frequency
                    self.set_rd_profile(current_thrd, current_interval,
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
