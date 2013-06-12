"""
Exports the Benchmark class, which is responsible for storing and plotting the
data corresponding to a benchmark. Utility class that is used by most scripts.
"""
import datetime as dt
import figure as fig
import itertools as it
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

    def __init__(self, name, num_threads, stack_type, num_sets=0, num_ways=0):
        """Constructor"""
        self.name = name
        self.num_threads = num_threads
        self.stack_type = stack_type
        self.num_sets = num_sets
        self.num_ways = num_ways
        assert (num_ways % num_threads == 0), \
            "Number of ways should be multiple of number of threads"
        self.ways = [x for x in xrange(1, num_ways + 1)]
        self.capacities = [x * num_sets for x in self.ways]
        self.ways.append(int(_MAGIC_MISS_DISTANCE))  # infinite capacity
        self.capacities.append(int(_MAGIC_MISS_DISTANCE))  # infinite capacity
        self.__thread_data = [_ThreadData() for 
            dummy in xrange(self.num_threads)]
        for thread_data in self.__thread_data:
            thread_data.miss_rate_all_intervals = dict()
            thread_data.rd_profiles = dict()
            thread_data.freq_v_cap = dict()
            thread_data.total_freq = dict()
    
    def set_rd_profile(self, thread, profile_id, rd_profile, tot_freq):
        """Store the list of reuse-distance frequencies for an id for a
        thread.
        """
        self.__thread_data[thread].rd_profiles[profile_id] = rd_profile
        self.__thread_data[thread].total_freq[profile_id] = tot_freq
    
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
                suffix = dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
            else:
                suffix = file_suffix + dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
            filename = self.name + "/" + self.name + "_t" + plot_id + "_rdp" + suffix
            subplots = len(data.rd_profiles)
            #if subplots > 6: subplots = 6
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
    
    def plot_rd_profiles_1_file(self, new_style=False, file_suffix=None):
        """Plot reuse-distance profile for all ids for all threads.
        
        One file for all threads. Each subplot is for an interval. Each subplot
        contains the lines for all threads together.
        X-axis denotes the number of reuse-distance bins and Y-axis denotes the
        frequency of accesses.
        """
        subplots = len(self.__thread_data[0].rd_profiles)
        #if subplots > 6: subplots = 6
        print "subplot: ", subplots
        subplots_per_page = subplots if subplots < 2 else 2
        if not(file_suffix):
            suffix = dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
        else:
            suffix = file_suffix + dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
        filename = self.name + "/" + self.name + "_all_rdp" + suffix
        figure = fig.Figure(filename,
                            figformat='pdf',
                            #title="RD Profile for all threads ",
                            total_subplots=subplots,
                            subplots_per_page=subplots_per_page,
                            font_size=6)
        for profile_id in self.__thread_data[0].rd_profiles:
            print "profile id: ", profile_id
            plot_data = list()
            legend_labels = list()
            all_keys = set()
            for data in self.__thread_data:
                all_keys.update(data.rd_profiles[profile_id].keys())
            all_keys_list = list(all_keys)    
            all_keys_list.sort(key=lambda x:float(x))
            for data in self.__thread_data:
                # Sort the rd_profile on distance
                # Distances in string, but sort on their values
                #sorted_bins =  data.rd_profiles[profile_id].keys()
                #sorted_bins.sort(key=lambda x:float(x))
                bins_list = list()
                freq_list = list()
                x_index = 0
                cum_freq = 0.0
                #cum_freq = 0
                tot_freq = data.total_freq[profile_id]
                for dist in all_keys_list:
                    bins_list.append(x_index)
                    x_index = x_index + 1
                    if dist in data.rd_profiles[profile_id]:
                        cum_freq += int(data.rd_profiles[profile_id][dist])
                        #freq_list.append(int(data.rd_profiles[profile_id][dist]))
                    else:
                       pass
                        #freq_list.append(0)
                    freq_list.append((tot_freq - cum_freq) / tot_freq)
                    #freq_list.append((tot_freq - cum_freq))
                bins = np.array(bins_list)
                rd_freq = np.array(freq_list)
                plot_data.append(bins)
                plot_data.append(rd_freq)
                plot_id = str(self.__thread_data.index(data))
                legend_labels.append("Thread " + plot_id)
            dist_labels = list()
            idx = 0
            for l in all_keys_list:
                val = float(l)
                if val == pow(2.00,idx):
                    if idx == 1:
                        dist_labels.append(' ')
                    else:
                        dist_labels.append(l)
                    idx += 1
                else:
                    dist_labels.append(' ')
            #dist_labels = all_keys_list    
            #legend_labels = ['Profile Id ' + str(profile_id)]
            sp = figure.add_plot(new_style, 
                                 legend_labels, 
                                 'Reuse Distance',
                                 'Miss Rate',
                                 ' ',
                                 #'Profile Id ' + str(profile_id), 
                                 dist_labels,
                                 *plot_data)    
            if profile_id >= subplots:
                break
        figure.save_and_close()

    def plot_rd_profiles_by_hit_type(self, file_suffix=None):
        """Plot reuse-distance profile for all ids for all threads.
        
        A separate file for each thread. Each subplot is for an interval.
        X-axis denotes the number of reuse-distance bins and Y-axis denotes the
        frequency of accesses. The frequency of accesses are further broken
        into accesses due to misses, local and foreign private hits, and local
        and foreign shared hits.
        """
        for data in self.__thread_data:
            plot_id = str(self.__thread_data.index(data))
            if not(file_suffix):
                suffix = dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
            else:
                suffix = file_suffix + dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
            filename = self.name + "/" + self.name + "_t" + plot_id + "_rdp_by_hits" + suffix
            subplots = len(data.rd_profiles)
            #if subplots > 2: subplots = 2
            print "subplot: ", subplots
            #subplots_per_page = subplots if subplots < 2 else 2
            subplots_per_page = 1
            figure = fig.Figure(filename,
                                figformat='pdf',
                                #title="RD Profile by Hit Status for thread " + plot_id,
                                total_subplots=subplots,
                                subplots_per_page=subplots_per_page,
                                font_size=6)
            for profile_id in data.rd_profiles:
                print "profile id: ", profile_id
                # Sort the rd_profile on distance
                # Distances in string, but sort on their values
                sorted_bins =  data.rd_profiles[profile_id].keys()
                sorted_bins.sort(key=lambda x:float(x))
                bins_list = list()
                freq_list_m = list()
                freq_list_p_l_h = list()
                freq_list_p_f_h = list()
                freq_list_s_l_h = list()
                freq_list_s_f_h = list()
                x_index = 0
                for dist in sorted_bins:
                    bins_list.append(x_index)
                    x_index += 1
                    freq_list_m.append(int(data.rd_profiles[profile_id][dist][0]))
                    freq_list_p_l_h.append(int(data.rd_profiles[profile_id][dist][1]))
                    freq_list_p_f_h.append(int(data.rd_profiles[profile_id][dist][2]))
                    freq_list_s_l_h.append(int(data.rd_profiles[profile_id][dist][3]))
                    freq_list_s_f_h.append(int(data.rd_profiles[profile_id][dist][4]))
                bins = np.array(bins_list)
                rd_freq_m = np.array(freq_list_m)
                rd_freq_p_l_h = np.array(freq_list_p_l_h)
                rd_freq_p_f_h = np.array(freq_list_p_f_h)
                rd_freq_s_l_h = np.array(freq_list_s_l_h)
                rd_freq_s_f_h = np.array(freq_list_s_f_h)
                plot_data = [bins, rd_freq_m, rd_freq_p_l_h, rd_freq_p_f_h,
                    rd_freq_s_l_h, rd_freq_s_f_h]
                dist_labels = sorted_bins
                legend_labels = ['Miss', 'Private Self-Hit',
                                 'Private Foreign Hit', 'Shared Self-Hit',
                                 'Shared Foreign Hit']
                sp = figure.add_stackedbar(legend_labels,
                                           'Reuse Distance',
                                           'References', 
                                           #'Profile Id ' + str(profile_id),
                                           '',
                                           dist_labels,
                                           *plot_data)    
                if profile_id >= subplots:
                    break

            figure.save_and_close()
    
    def read_rddata_from_file(self, bmfile, num_threads, offset=0, quantum_size=1):
        """Read reuse distance profile data from file."""
        IsInterval = lambda line: line.startswith("Interval")
        IsThread = lambda line: line.startswith("thread")
        IsHistogram = lambda line: line.startswith("histogram")
        IsShared = lambda line: line.startswith("Shared")
        IsPrivate = lambda line: line.startswith("Private")
 
        # Initialization
        current_interval = profile_id = 0
        profile_id_offset = 0 if offset == 0 else 1;
        current_thrd = 0
        stack_type = None
        rd_profiles = [dict() for dummy in xrange(num_threads)]
        total_freq = [0 for dummy in xrange(num_threads)]
        with open(bmfile, 'r') as src:
            for line in src:
                if IsInterval(line):
                    current_interval = current_interval + 1
                
                elif IsThread(line):
                    current_thrd = int(line.split(':', 1)[1])

                elif IsShared(line):
                    stack_type = "shared"
                    assert self.stack_type != None, "stack type in input \
                            file: shared, stack type specified: None"

                elif IsPrivate(line):
                    stack_type = "private"
                    assert stack_type != None, "stack type in input \
                            file: private, stack type specified: None"

                elif IsHistogram(line):
                    if stack_type != self.stack_type:
                        continue
                    histo_line = line[11:-2]
                    token_list = histo_line.split()
                    for token in token_list:
                        token = token.rstrip(',')
                        subtokens = token.split(':')
                        distance = '%.2f' %float(subtokens[0])
                        if len(subtokens) == 2:
                            frequency = subtokens[1]
                            total_freq[current_thrd] += int(frequency)
                        else:
                            frequency = [subtokens[i] 
                                for i in xrange(1, len(subtokens))]
                            for f in frequency:
                                total_freq[current_thrd] += int(f)
                        if float(distance) < _MAGIC_MISS_DISTANCE:
                            if distance in rd_profiles[current_thrd]:
                                old_freq = rd_profiles[current_thrd][distance]
                                if isinstance(old_freq, list):
                                    rd_profiles[current_thrd][distance] = [str(int(x) + int(y))
                                        for x,y in zip(old_freq, frequency)]
                                else:
                                    rd_profiles[current_thrd][distance] = str(int(frequency) +
                                        int(old_freq))
                            else:
                                rd_profiles[current_thrd][distance] = frequency
                            #sum_f += int(frequency)
                    #print "freq sum for thread", current_thrd, sum_f
                    if current_interval < offset: continue
                    if quantum_size == 1:
                        to_save = 0
                    else:
                        to_save = (current_interval - offset) % quantum_size
                    if to_save == 0:
                        profile_id = ((current_interval - offset) / quantum_size) + profile_id_offset
                        print 'to save', current_interval, profile_id
                        self.set_rd_profile(current_thrd, profile_id,
                                        rd_profiles[current_thrd], total_freq[current_thrd])
                        rd_profiles[current_thrd] = dict()
                        total_freq[current_thrd] = 0
                
                else:
                    pass  # other cases are not relevant
            for i in xrange(num_threads):
                if rd_profiles[i]:
                    profile_id = ((current_interval - offset) / quantum_size) + profile_id_offset + 1
                    print 'to save', current_interval, profile_id
                    self.set_rd_profile(i, profile_id,
                                    rd_profiles[i], total_freq[i])
    
    def read_rddata_from_file_2phase(self, bmfile, num_threads, offset=0, quantum_size=1, start_thread=0):
        """Read reuse distance profile data from file."""
        IsInterval = lambda line: line.startswith("Interval")
        IsThread = lambda line: line.startswith("thread")
        IsHistogram = lambda line: line.startswith("histogram")
        IsShared = lambda line: line.startswith("Shared")
        IsPrivate = lambda line: line.startswith("Private")
 
        # Initialization
        current_interval = profile_id = 0
        current_thrd = 0
        stack_type = None
        epoch_size = quantum_size * num_threads
        preferred_status = 0
        preferred_threads = list()
        p_thread = start_thread
        for i in xrange(epoch_size):
            if (i > 0) and (i % quantum_size == 0):
                p_thread = (p_thread + 1) % num_threads
            preferred_threads.append(p_thread)
        print 'preferred threads', preferred_threads
        rd_profiles_p = [dict() for dummy in xrange(num_threads)]
        rd_profiles_u = [dict() for dummy in xrange(num_threads)]
        with open(bmfile, 'r') as src:
            for line in src:
                if IsInterval(line):
                    current_interval = current_interval + 1
                
                elif IsThread(line):
                    current_thrd = int(line.split(':', 1)[1])
                    if current_interval <= offset:
                        preferred_status = 0
                    else:
                        age_in_epoch = (current_interval - offset - 1) % epoch_size
                        if preferred_threads[age_in_epoch] == current_thrd:
                            preferred_status = 1
                        else:
                            preferred_status = 2

                elif IsShared(line):
                    stack_type = "shared"
                    assert self.stack_type != None, "stack type in input \
                            file: shared, stack type specified: None"

                elif IsPrivate(line):
                    stack_type = "private"
                    assert stack_type != None, "stack type in input \
                            file: private, stack type specified: None"

                elif IsHistogram(line):
                    if stack_type != self.stack_type:
                        continue
                    if preferred_status == 0:
                        continue  # Before offset
                    histo_line = line[11:-2]
                    token_list = histo_line.split()
                    for token in token_list:
                        token = token.rstrip(',')
                        subtokens = token.split(':')
                        distance = '%.2f' %float(subtokens[0])
                        if len(subtokens) == 2:
                            frequency = subtokens[1]
                        else:
                            frequency = [subtokens[i] 
                                for i in xrange(1, len(subtokens))]
                        if float(distance) < _MAGIC_MISS_DISTANCE:
                            if preferred_status == 1:
                                if distance in rd_profiles_p[current_thrd]:
                                    old_freq = rd_profiles_p[current_thrd][distance]
                                    if isinstance(old_freq, list):
                                        rd_profiles_p[current_thrd][distance] = [str(int(x) + int(y))
                                            for x,y in zip(old_freq, frequency)]
                                    else:
                                        rd_profiles_p[current_thrd][distance] = str(int(frequency) +
                                            int(old_freq))
                                else:
                                    rd_profiles_p[current_thrd][distance] = frequency
                            elif preferred_status == 2:
                                if distance in rd_profiles_u[current_thrd]:
                                    old_freq = rd_profiles_u[current_thrd][distance]
                                    if isinstance(old_freq, list):
                                        rd_profiles_u[current_thrd][distance] = [str(int(x) + int(y))
                                            for x,y in zip(old_freq, frequency)]
                                    else:
                                        rd_profiles_u[current_thrd][distance] = str(int(frequency) +
                                            int(old_freq))
                                else:
                                    rd_profiles_u[current_thrd][distance] = frequency
                            else:
                                assert 0, "Flow should not come here"
                
                else:
                    pass  # other cases are not relevant
            for i in xrange(num_threads):
                profile_id = 1
                self.set_rd_profile(i, profile_id, rd_profiles_p[i], 0)
                profile_id = 2 
                self.set_rd_profile(i, profile_id, rd_profiles_u[i], 0)

    def build_freq_vs_ways_profile(self):
        """For each thread & interval build cdf of freq vs number of ways."""
        for t, tdata in enumerate(self.__thread_data):
            for profile_id, rd_profile in tdata.rd_profiles.iteritems():
                freq_cdf = [0 for dummy in xrange(len(self.ways))]
                running_total = running_idx = 0
                sorted_keys = sorted(rd_profile.iterkeys(), key=lambda x: float(x))
                for dist in sorted_keys:
                    freq = rd_profile[dist]
                    while (float(dist) >= self.ways[running_idx]):
                        freq_cdf[running_idx] = running_total
                        running_idx += 1
                    running_total += int(freq)
                while running_idx < len(self.ways):
                    freq_cdf[running_idx] = running_total
                    running_idx += 1
                self.set_freq_cdf(t, profile_id, freq_cdf)
    
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

    def all_possible_partitions(self):
        """Create a list of all possible partitions so that each partition
        has at least 1 way."""
        to_partition = self.num_ways - self.num_threads
        leftmost = -1
        rightmost = to_partition + self.num_threads - 1
        positions = [x for x in xrange(rightmost)]
        p_configs = it.combinations(positions, self.num_threads - 1)
        partitions= [[8,8,8,8], [11,7,7,7], [14,6,6,6], [17,5,5,5],
                     [20,4,4,4], [23,3,3,3], [26,2,2,2], [29,1,1,1]]
        partition_labels= ['8-8-8-8', '11-7-7-7', '14-6-6-6', '17-5-5-5',
                           '20-4-4-4', '23-3-3-3', '26-2-2-2', '29-1-1-1']
        """partitions= [[8,8,8,8], [9,9,9,5], [10,10,10, 2],
                     [11,11,5,5], [12,12,4,4], [13,13,3,3],
                     [14,14,2,2], [15,15,1,1], [11,7,7,7],
                     [14,6,6,6], [17,5,5,5], [20,4,4,4],
                     [23,3,3,3], [26,2,2,2], [29,1,1,1]]
        partition_labels= ['8', '9', '10,2',
                     '11,5', '12,4', '13,3',
                     '14,2', '15,1', '11,7',
                     '14,6', '17,5', '20,4',
                     '23,3', '26,2,', '29,1,']"""
        #partitions = []
        #for config in p_configs:
            #new_p = []
            #left = right = leftmost
            #for x in config:
                #right = x
                #new_p.append(right - left) # -1 + 1 cancels
                #left = right
            #new_p.append(rightmost - left)
            #partitions.append(new_p)
        return partitions, partition_labels

    def plot_partition_v_misses(self, new_style=False, file_suffix=None):
        """For each interval for each thread as preferred thread, plot the
        misses for all possible partitions.
        """
        partitions, partition_labels = self.all_possible_partitions()
        subplots = num_profiles = len(self.__thread_data[0].freq_v_cap)
        #if subplots > 6: subplots = 6
        print "subplot: ", subplots
        subplots_per_page = subplots if subplots < 2 else 2
        if not(file_suffix):
            suffix = dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
        else:
            suffix = file_suffix + '_' + dt.datetime.now().strftime("%y_%m_%d_%H:%M:%S")
        filename = self.name + "/" + self.name + suffix
        figure = fig.Figure(filename,
                            figformat='pdf',
                            #title="RD Profile for all threads ",
                            total_subplots=subplots,
                            subplots_per_page=subplots_per_page,
                            font_size=6)
        best_allocations = list()
        for profile_id in xrange(1, num_profiles + 1):
            print "profile id: ", profile_id
            plot_data = list()
            legend_labels = list()
            all_keys = set()
            best_allocations_per_profile = list()
            for preferred_t in xrange(self.num_threads):
                sys.stdout.write("Preferred thread: %d\n" % preferred_t)
                min_misses = 4611686018427387904
                best_alloc = []
                x_list = list()
                y_list = list()
                x_index = 0
                for alloc in partitions:
                    x_list.append(x_index)
                    x_index += 1
                    total_misses = 0
                    index = 0
                    for x in alloc:
                        current_t = (preferred_t + index) % self.num_threads
                        total_misses += self.get_misses(current_t, profile_id, x)
                        index += 1
                    y_list.append(total_misses)    
                    if total_misses < min_misses:
                        min_misses = total_misses
                        best_alloc = alloc
                x_array = np.array(x_list)
                y_array = np.array(y_list)
                plot_data.append(x_array)
                plot_data.append(y_array)
                plot_id = str(preferred_t)
                legend_labels.append("Thread " + plot_id)
                best_allocations_per_profile.append(best_alloc)
                sys.stdout.write("Best Alloc for Interval %d: %s\n" % 
                    (profile_id, str(best_alloc)))
                print 'misses: ', y_array
            sp = figure.add_plot(new_style,
                                 legend_labels, 
                                 'Allocations',
                                 'Misses',
                                 ' ',
                                 #'Profile Id ' + str(profile_id), 
                                 partition_labels,
                                 *plot_data)    
            if profile_id >= subplots:
                break
            best_allocations.append(best_allocations_per_profile)
        figure.save_and_close()
        return best_allocations
    
    def get_misses(self, thread, profile_id, ways):
        "Return the hits for a particular way"""
        ret_val = self.__thread_data[thread].freq_v_cap[profile_id][len(self.ways) - 1]
        if ways > 0:
            ret_val = ret_val - self.__thread_data[thread].freq_v_cap[
                profile_id][ways - 1]
        return ret_val
     
    def find_best_partition(self,shared_profile=None):
        """For each interval for each thread as preferred thread, find the
        best possible partition. If a shared profile is supplied, use that
        to find the best partition for the hybrid case."""
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
                    ave_neg_gain = float(neg_gain) / (self.num_threads - 1)
                    #print "ave ng:", ave_neg_gain
                    gain = pos_gain + ave_neg_gain
                    if gain > max_gain:
                        max_gain = gain
                        best_alloc = preferred_alloc
                    preferred_alloc += (self.num_threads - 1)
                    other_alloc -= 1
                # check for the final best_allocation cosidering shared RD
                new_best_alloc = best_alloc
                #print "private best alloc: ", new_best_alloc
                if shared_profile != None:
                    max_gain = 0
                    preferred_alloc = best_alloc + (self.num_threads - 1)
                    other_alloc = ((self.num_ways - best_alloc) /
                        (self.num_threads - 1))
                    print "other alloc: ", other_alloc
                    new_other_alloc = other_alloc - 1
                    while (preferred_alloc <= max_alloc):
                        shared_gain= sum(shared_profile.gain(t, profile_id + 1,
                                         0, preferred_alloc - best_alloc)
                            for t in xrange(self.num_threads))
                        print "shared_gain ", shared_gain
                        pos_gain = shared_gain
                        neg_gain = sum(self.gain(t, profile_id + 1,
                                       other_alloc, new_other_alloc)
                            for t in xrange(self.num_threads) if t != preferred_t)
                        ave_neg_gain = float(neg_gain) / (self.num_threads - 1)
                        print "ave ng:", ave_neg_gain
                        gain = pos_gain + ave_neg_gain
                        print "gain:", gain
                        if gain > max_gain:
                            max_gain = gain
                            new_best_alloc = preferred_alloc
                        preferred_alloc += (self.num_threads - 1)
                        new_other_alloc -= 1
                best_allocations_per_thread.append(new_best_alloc)
                sys.stdout.write("Best Alloc for Interval %d: %d\n" % 
                    (profile_id + 1, new_best_alloc))
            best_allocations.append(best_allocations_per_thread)
        return best_allocations

    def gain(self, thread, profile_id, from_alloc, to_alloc):
        "Return the gain obtained between two allocations"""
        value_for_from_alloc = value_for_to_alloc = 0
        if from_alloc > 0:
            value_for_from_alloc = self.__thread_data[thread].freq_v_cap[
                profile_id][from_alloc - 1]
        if to_alloc > 0:
            value_for_to_alloc = self.__thread_data[thread].freq_v_cap[
                profile_id][to_alloc - 1]
        return value_for_to_alloc - value_for_from_alloc

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
                                        rd_profile, 0)
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
