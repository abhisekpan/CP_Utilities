"""Coming Later

"""

"""Additional Info

Created on Oct 28, 2011
@author: Abhisek

"""
import sys
import benchmark as bm
import plot_data as pd


def analyze():
    """ """
    #=======================================================================
    # command line processing
    #=======================================================================
    if len(sys.argv) != 4:
        sys.stdout.write("Incorrect number of arguments. Program description:\n" 
                         + __doc__)
        sys.exit(1)
                
    benchmarks_to_analyze = sys.argv[1].split(',')
    file_names = sys.argv[2].split(',')
    num_threads = int(sys.argv[3])
    
    bm_list = list()
    for program_name in benchmarks_to_analyze:
        new_bm = bm.Benchmark(program_name, num_threads)
        bmfile = file_names[benchmarks_to_analyze.index(program_name)]
        new_bm.read_from_file(bmfile)
        new_bm.plot_mr_v_interval(new_style=False)
        bm_list.append(new_bm)
        
    #pd.plot_mr_v_interval(bm_list, "bm_v_interval.eps", same_axis=False)
    sys.stderr.write("my work is done here\n")

if __name__ == '__main__':
    analyze()
