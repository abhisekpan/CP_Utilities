#! /usr/bin/env python
"""Finds the best partition of total cache space for each interval.

NAME
    best_partition.py

SYNOPSYS
    ./best_partition.py benchmark input_file num_threads set_bits total_ways
    is hybrid

DESCRIPTION
    Given the reuse-distance signatures of each thread for each interval for
    a benchmark, finds the best partition possible partition after choosing a
    priority thread. Each thread is chosen as a priority thread in turn. The
    algorithm starts by dividing the total allocation equally among all
    threads. Then the allocation of the preferred thread is increased by (n-1)
    where n = number of threads. The allocation for all other threads is
    reduced by 1. The algorithm computes the gain for this allocation, the gain
    being equal to the references included by increasing the allocation in the
    preferred thread minus the references left out by reducing the allocaion
    in all other threads. This step is repeated till the allocation for the
    other threads reduces to 1. The allocation which shows the maximum gain
    is chosen as the best allocation for a particular preferred thread.
    
    For hybrid scheme, the algorithm considers both shared and private reuse
    distance profiles. According to our observations, shared blocks are better
    utilized when they are allocated in the preferred partition, since these
    blocks can stay in this partition for longer time. So in hybrid sheme, we
    consider the shared reuse distance profile and the references included in
    the shared profile, starting from dist 0, are also included in the gain in
    allocating ways to the preferred thread. So for example, when 3 extra ways
    are allocated to the preferred thread beyond its normal allocation, the
    references with distance less than 3 in the shared profile are also
    considered in the gain obtained.
 
OPTIONS
    benchmark
        Benchmark name

    input_file
        Input file containing reuse-distance signatures per interval. This has
        to be the output of the reuse distance tool, using Pin or simics.

    num_threads
        Number of threads.
    
    set_bits
        Number of sets per way, in terms of container bits. 8 bits => 2^8 sets.

    total_ways
        Total number of ways for all threads. Should be divisible by number of
        threads.
    
    is_hybrid
        Are we processing hybrid reuse distance. That would require 2 stacks.
        0 = no, 1 = yes.
                       
EXAMPLES
    ./best_partition.py  blackscholes inter_rda_blackscholes_large_4_5mil.out 4
    9 32 0

NOTES

AUTHOR
    Abhisek Pan, pana@purdue.edu

LICENSE
    Copyright (C) 2012  Abhisek Pan, Purdue University. All rights reserved.

    This file is distributed under the University of Illinois/NCSA Open Source
    License. 
    You can obtain a soft copy of the license either by visiting
    http://otm.illinois.edu/uiuc_openSource, or by mailing pana@purdue.edu.

VERSION
    1.0
"""

import sys
import benchmark as bm

def best_partition():
    """See script description."""
    #=======================================================================
    # command line processing
    #=======================================================================
    if len(sys.argv) != 7:
        sys.stdout.write("Incorrect number of arguments. Program description:\n" 
                         + __doc__)
        sys.exit(1)
    benchmark = sys.argv[1]
    input_file = sys.argv[2]
    num_threads = int(sys.argv[3])
    num_sets = 2 ** int(sys.argv[4])
    num_ways = int(sys.argv[5])
    is_hybrid = int(sys.argv[6])
    if not(is_hybrid):
        stack_type = None
        new_bm = bm.Benchmark(benchmark, num_threads, stack_type,
                              num_sets, num_ways)
        new_bm.read_rddata_from_file(input_file, num_threads)
        new_bm.build_freq_vs_capacity_profile()
        _ = new_bm.find_best_partition()
    else:
        stack_type = 'private'
        new_bm_p = bm.Benchmark(benchmark, num_threads, stack_type,
                                num_sets, num_ways)
        new_bm_p.read_rddata_from_file(input_file, num_threads)
        new_bm_p.build_freq_vs_capacity_profile()
        
        stack_type = 'shared'
        new_bm_s = bm.Benchmark(benchmark, num_threads, stack_type,
                              num_sets, num_ways)
        new_bm_s.read_rddata_from_file(input_file, num_threads)
        new_bm_s.build_freq_vs_capacity_profile()
        _ = new_bm_p.find_best_partition(shared_profile=new_bm_s)
    sys.stderr.write("my work is done here\n")


if __name__ == '__main__':
    best_partition()

