#! /usr/bin/env python
"""Plots reuse distance signatures for each interval.

NAME
    rda_plot.py

SYNOPSYS
    ./rda_plot.py benchmark input_file num_threads

DESCRIPTION
    Given the reuse-distance signatures for each intervals for a benchmark,
    plots the reuse distance signature for each interval in a subplot. Ouputs
    one file per thread.
 
OPTIONS
    benchmark
        Benchmark name

    input_file
        Input file containing reuse-distance signatures per interval. This has
        to be the output of the reuse distance Pintool.
    num_threads
        Number of threads.
                       
EXAMPLES
    ./rda_plot.py  blackscholes inter_rda_blackscholes_large_4_5mil.out 4

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
import plot_data as pd


def rda_plot():
    """Plot rd signature for the benchmark given as input."""
    #=======================================================================
    # command line processing
    #=======================================================================
    if len(sys.argv) != 4:
        sys.stdout.write("Incorrect number of arguments. Program description:\n" 
                         + __doc__)
        sys.exit(1)
    benchmark = sys.argv[1]
    input_file = sys.argv[2]
    num_threads = int(sys.argv[3])
    new_bm = bm.Benchmark(benchmark, num_threads)
    new_bm.read_rddata_from_file(input_file)
    new_bm.plot_rd_profiles(new_style=False)
    sys.stderr.write("my work is done here\n")


if __name__ == '__main__':
    rda_plot()

