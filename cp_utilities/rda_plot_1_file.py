#! /usr/bin/env python
"""Plots reuse distance signatures for each interval. All plots in 1 file.

NAME
    rda_plot_1_file.py

SYNOPSYS
    ./rda_plot_1_file.py benchmark input_file num_threads is_hybrid offset
    quantum_size

DESCRIPTION
    Given the reuse-distance signatures for each interval for a benchmark,
    plots the reuse distance signature for each interval in a subplot. Outputs
    only a single file for all threads.
 
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
    
    offset
        Offset after which partitioning started while this profile was
        collected

    quantum_size
        Size of intervals each quantum in round robin partitioning
                       
EXAMPLES
    ./rda_plot_1_file.py blackscholes inter_rda_blackscholes_large_4_5mil.out 4 0
    1 23

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


def rda_plot_1_file():
    """Plot rd signature for the benchmark given as input."""
    #=======================================================================
    # command line processing
    #=======================================================================
    if not(len(sys.argv) == 7):
        sys.stdout.write("Incorrect number of arguments. Program description:\n" 
                         + __doc__)
        sys.exit(1)
    benchmark = sys.argv[1]
    input_file = sys.argv[2]
    num_threads = int(sys.argv[3])
    is_hybrid = int(sys.argv[4])
    offset = int(sys.argv[5])
    quantum_size = int(sys.argv[6])
    if not(is_hybrid):
        stack_type = None
        new_bm = bm.Benchmark(benchmark, num_threads, stack_type)
        new_bm.read_rddata_from_file(input_file, num_threads, offset, quantum_size)
        new_bm.plot_rd_profiles_1_file(new_style=False)
        sys.stderr.write("my work is done here\n")
    else:
        stack_type = "private"
        new_bm_p = bm.Benchmark(benchmark, num_threads, stack_type)
        new_bm_p.read_rddata_from_file(input_file, num_threads, offset, quantum_size)
        new_bm_p.plot_rd_profiles_1_file(new_style=False,
                                  file_suffix=stack_type)
        stack_type = "shared"
        new_bm_s = bm.Benchmark(benchmark, num_threads, stack_type)
        new_bm_s.read_rddata_from_file(input_file, num_threads, offset, quantum_size)
        new_bm_s.plot_rd_profiles_1_file(new_style=False,
                                  file_suffix=stack_type)
        sys.stderr.write("my work is done here\n")


if __name__ == '__main__':
    rda_plot_1_file()

