"""
Unit tests for the benchmark module.
"""

import cp_utilities.benchmark as bm
import errno # file does not exist error
import os
import sys

def setUpModule():
    pass
    

class Test_find_best_partition_basic_algo(object):
    """Contains data-driven tests to check the algorithm for choosing the
    best partition given the frequency vs capacity histograms. Doesnot
    check for multiple histograms. Considers 2 threads only."""
    def setUp(self):
        self.Initialize()
        self.testbm = bm.Benchmark("test_bm", self.numthreads, self.numsets,
                                    self.numways)

    def Initialize(self):
        self.numsets = 2
        self.numways = 16
        self.numthreads = 2 
    
    def make_freq_vs_capacities(self):
        self.testdata = list()
        num_capacities = self.numways + 1
        # case 0
        freq_pdf = [0 for dummy in xrange(num_capacities)]
        best_alloc = [[8], [8]] 
        freq_pdf[0] = 100
        freq_cdf = [x for x in self.cumsum(freq_pdf)]
        self.testdata.append((freq_cdf, best_alloc))
        # case 1
        freq_pdf = [0 for dummy in xrange(num_capacities)]
        best_alloc = [[11],[11]]
        freq_pdf[0] = freq_pdf[10] = 100
        freq_cdf = [x for x in self.cumsum(freq_pdf)]
        self.testdata.append((freq_cdf, best_alloc))
        # case 2
        freq_pdf = [0 for dummy in xrange(num_capacities)]
        best_alloc = [[8],[8]]
        freq_pdf[5] = freq_pdf[10] = 100
        freq_cdf = [x for x in self.cumsum(freq_pdf)]
        self.testdata.append((freq_cdf, best_alloc))
        # case 3
        freq_pdf = [0 for dummy in xrange(num_capacities)]
        best_alloc = [[10],[10]]
        freq_pdf[5] = freq_pdf[9] = 100
        freq_cdf = [x for x in self.cumsum(freq_pdf)]
        self.testdata.append((freq_cdf, best_alloc))
        # case 4
        freq_pdf = [0 for dummy in xrange(num_capacities)]
        best_alloc = [[15],[15]]
        for i in xrange(num_capacities):
            if i < self.numways / self.numthreads:
                freq_pdf[i] = 10
            else:
                freq_pdf[i] = 200
        freq_cdf = [x for x in self.cumsum(freq_pdf)]
        self.testdata.append((freq_cdf, best_alloc))
        # case 5
        freq_pdf = [0 for dummy in xrange(num_capacities)]
        best_alloc = [[8],[8]]
        freq_pdf[0] = 10
        freq_pdf[self.numways - 1] = 100
        freq_cdf = [x for x in self.cumsum(freq_pdf)]
        self.testdata.append((freq_cdf, best_alloc))
    
    def cumsum(self, seq):
        """Cumulative sum for a sequence, to convert fd to cd."""
        s= 0
        for c in seq:
            s+= c
            yield s

    def test_all_find_best_parition_cases(self):
        self.Initialize()
        self.make_freq_vs_capacities()
        for d in self.testdata:
            yield self.check_find_best_partition, d[0], d[1]

    def check_find_best_partition(self, inp, target_output):
        for t in xrange(self.numthreads):
            self.testbm.set_freq_cdf(t, 1, inp)
        test_output = self.testbm.find_best_partition()
        try:
            assert (test_output == target_output)
        except AssertionError as err:
            print "test_op", test_output
            print "target_op", target_output
            print(err)
            raise


class Test_build_freq_vs_capacity_profile_basic_algo(object):
    """Contains data-driven tests to check if the algorithm for converting
    reuse distance histograms to capacity_vs_frequency cdfs is correct.
    Doesnot check for things like multiple threads or multiple intervals.
    """

    def setUp(self):
        self.Initialize()
        self.testbm = bm.Benchmark("test_bm", self.numthreads, self.numsets,
                                    self.numways)

    def Initialize(self):
        self.numsets = 2
        self.numways = 16
        self.numthreads = 1
        self.input_file = "input.txt"

    def make_testdata(self):
        self.testdata = list()
        num_capacities = self.numways + 1
        # case 0
        self.testdata.append((
            {'0.00':'100'},
            [100] * num_capacities))
        # case 1
        self.testdata.append((
            {'16.00':'100'},
            [0] * 8 + [100] * (num_capacities - 8)))
        # case 2
        self.testdata.append((
            {'2.00':'100'},
            [0] * 1 + [100] * (num_capacities - 1)))
        # case 3
        self.testdata.append((
            {'1500.00':'100'},
            [0] * (num_capacities - 1) + [100]))
        # case 4
        inputs = dict()
        outputs = list()
        for i in xrange(0,32):
            inputs[str(float(i))] = '100'
        for i in xrange(0,16):
            outputs.append(200 * (i + 1))
        outputs.append(3200)
        self.testdata.append((inputs, outputs))
        # case 5
        inputs = dict()
        outputs = list()
        for i in xrange(1,33):
            inputs[str(float(i))] = '100'
        outputs.append(100)
        for i in xrange(0,15):
            outputs.append(200 * (i + 1) + 100)
        outputs.append(3200)
        self.testdata.append((inputs, outputs))
        # case 6
        inputs = dict()
        outputs = list()
        for i in xrange(0,40):
            inputs[str(float(i))] = '100'
        for i in xrange(0,16):
            outputs.append(200 * (i + 1))
        outputs.append(4000)
        self.testdata.append((inputs, outputs))

    def test_all_freq_v_caps(self):
        self.Initialize()
        self.make_testdata()
        for d in self.testdata:
            #make input files from input testdata
            self.create_input_file(d[0])
            yield self.check_freq_v_cap, d[1]
    
    def check_freq_v_cap(self, target_output):
        self.testbm.read_rddata_from_file(self.input_file)
        self.testbm.build_freq_vs_capacity_profile()
        test_output = self.testbm.get_freq_cdf(0,1)
        try:
            assert (test_output == target_output)
        except AssertionError as err:
            print "test_op", test_output
            print "target_op", target_output
            print(err)
            raise

    def create_input_file(self, input_data):
        with open(self.input_file, 'w') as f:
            f.write('Interval:1\n')
            f.write('thread:0\n')
            f.write('histogram:{')
            histo_list = list()
            sorted_keys = sorted(input_data.iterkeys(), key=lambda x: float(x))
            for dist in sorted_keys:
                freq = input_data[dist]
                histo_list.append('%s:%s' % (dist,freq))
            histo_string = ', '.join(histo_list)
            #print "histo_string: ", histo_string
            f.write(histo_string + '}\n')
    
    def tearDown(self):
        try:
            os.remove(self.input_file)
        except OSError as e:
            # errno.ENOENT = no such file or directory
            if e.errno != errno.ENOENT: raise


def tearDownModule():
    pass

