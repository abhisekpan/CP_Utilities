#! /usr/bin/env python
"""Plots reuse distance signatures for each interval.

NAME
    rda_plot.py

SYNOPSYS
    ./rda_plot.py benchmark input_file num_threads is_hybrid [filter_capacity]

DESCRIPTION
    Given the reuse-distance signatures for each interval for a benchmark,
    plots the reuse distance signature for each interval in a subplot. Outputs
    one file per thread.
 
OPTIONS
    benchmark
        Benchmark name

    input_file
        Input file containing reuse-distance signatures per interval. This has
        to be the output of the reuse distance tool, using Pin or simics.

    num_threads
        Number of threads.

    is_hybrid
        Are we processing hybrid reuse distance. That would require 2 stacks.
        0 = no, 1 = yes.
    
    filter_capacity
        Capacity of the reuse distance filter, if any. Optional
                       
EXAMPLES
    ./rda_plot.py  blackscholes inter_rda_blackscholes_large_4_5mil.out 4
    512

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


def rda_plot():
    """Plot rd signature for the benchmark given as input."""
    #=======================================================================
    # command line processing
    #=======================================================================
    if not(5 <= len(sys.argv) <= 6):
        sys.stdout.write("Incorrect number of arguments. Program description:\n" 
                         + __doc__)
        sys.exit(1)
    benchmark = sys.argv[1]
    input_file = sys.argv[2]
    num_threads = int(sys.argv[3])
    is_hybrid = int(sys.argv[4])
    filter_distance = 0.0
    if len(sys.argv) == 6: filter_distance = float(sys.argv[5])
    if not(is_hybrid):
        stack_type = None
        new_bm = bm.Benchmark(benchmark, num_threads, stack_type)
        new_bm.read_rddata_from_file(input_file)
        new_bm.plot_rd_profiles(new_style=False, filter_distance=filter_distance)
        sys.stderr.write("my work is done here\n")
    else:
        stack_type = "private"
        new_bm_p = bm.Benchmark(benchmark, num_threads, stack_type)
        new_bm_p.read_rddata_from_file(input_file)
        new_bm_p.plot_rd_profiles(new_style=False,
                                  filter_distance=filter_distance,
                                  file_suffix=stack_type)
        stack_type = "shared"
        new_bm_s = bm.Benchmark(benchmark, num_threads, stack_type)
        new_bm_s.read_rddata_from_file(input_file)
        new_bm_s.plot_rd_profiles(new_style=False,
                                  filter_distance=filter_distance,
                                  file_suffix=stack_type)
        sys.stderr.write("my work is done here\n")


if __name__ == '__main__':
    rda_plot()

