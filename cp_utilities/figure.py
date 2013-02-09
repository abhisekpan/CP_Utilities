'''
Created on Oct 27, 2011

@author: pana
'''

import math
import matplotlib.pyplot as pl
from itertools import cycle


_inches_per_pt = 1.0 / 72.27               # Convert pt to inch
_golden_mean = (math.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
_lines = ["-", "--", "-.", ":"]
_linecycler = cycle(_lines)


class Figure(object):
    
    """ Handles the plotting environment and the actual plotting for a figure. 
    
    This class acts as a wrapper around the matplotlib. Matplotlib provides
    too many options! This class restricts those choices and makes it a little 
    easier for me to handle. The figure will be plotted in one file. 
    There can be multiple sub-plots in the figure. When all plots are added, 
    the figure should be saved and closed.
    """    
    
    def __init__(self, filename, title=None, columns=1, num_subplots=1,
                 fig_width_pt=500.0, font_size=9, title_font_size=11):
        """Initialize the plotting environment. 
        
        @param filename: file name where figure will be plotted
        @param title: Title of the figure
        @param columns: number of columns
        @param num_subplots: total number of sub-plots in this figure
        @param fig_width_pt: width of one column in pixels, 
        @param font_size: font size for everything except title
        @param title_font_size: font size for title
        
        Get the column width in pixels from LaTeX using \showthe\columnwidth.
        This sets some common parameters for the figure, such as font and figure
        sizes. The size of one sub-plot is determined from the parameters. 
        The size of the figure is then set from that and the total number of 
        sub-plots.
        
        """
        self.filename = filename
        self.total_subplots = num_subplots
        self.total_columns = columns
        self.total_rows = int(math.ceil(self.total_subplots / 
                                        self.total_columns))
        self.current_plot = 1
        fig_width_in = fig_width_pt * _inches_per_pt * self.total_columns # width in inches
        fig_height_in = fig_width_in * _golden_mean * self.total_rows # height in inches
        fig_size = [fig_width_in, fig_height_in]
        self.plot_params = {'backend': 'ps',
               'axes.labelsize': font_size,
               'text.fontsize': font_size,
               'legend.fontsize': font_size,
               'xtick.labelsize': font_size,
               'ytick.labelsize': font_size,
               'text.usetex': True,
               'figure.figsize': fig_size}
        pl.rcParams.update(self.plot_params)
        self.figure = pl.figure()
        self.figure.suptitle(title, fontsize=title_font_size)

    def set_plot_param(self, subplot, xlabel=None, ylabel=None, title=None,
                        rect=[0.1, 0.15, 0.8, 0.7], legend=True, legend_loc=5):
        """Add a new axis with parameters and return the axis.
        @param subplot: the subplot for which the axis is set 
        @param xlabel: label for x axis
        @param ylabel: label for y axis
        @title title of the figure using this axis
        @param rect: space between the axes and the end of fig  -
        [left, bottom, width, height] in normalized (0, 1) units.
        @param legend: control printing of legends. 
        @param legend_loc: location of the legend. defaults is on the right 
        
        The location codes for legend are
        Location String 	Location Code
        'best'    0
    	'upper right'	1
    	'upper left'	2
    	'lower left'	3
    	'lower right'	4
    	'right'	5
    	'center left'	6
    	'center right'	7
    	'lower center'	8
    	'upper center'	9
    	'center'	10

        """
        #subplot.set_position(rect)
        if xlabel:  subplot.set_xlabel(r'\textit{' + xlabel + '}')
        if ylabel:  subplot.set_ylabel(r'\textit{' + ylabel + '}')
        if title:   subplot.set_title(title.encode('string-escape'))
        if legend:  subplot.legend(loc=legend_loc)

    def add_plot(self, new_style=False, labels=None, * args, **kwargs):
        """Add a new sub-plot to the figure"""
        assert self.current_plot <= self.total_subplots, \
        "too many sub-plots in this figure!"

        if new_style == True: 
            kwargs['linestyle'] = next(_linecycler)
        else:
            kwargs['linestyle'] = _lines[0]      # solid line by default
        sp = self.figure.add_subplot(self.total_rows, self.total_columns, self.current_plot)
        self.set_plot_param(sp, legend=False)
        lines = sp.plot(*args, **kwargs)
        if labels:
            dummy = [line.set_label(label) for line, label in zip(lines, labels)]
                
        self.current_plot += 1
        return sp
    
    def save(self):
        """Save the figure in a file"""
        self.figure.savefig(self.filename)
    
    def close(self):
        """ close the figure and free resources."""
        pl.close(self.figure)
         
#pl.tight_layout(pad=1.2)
#pl.subplots_adjust(bottom=0.1, top=0.9, left=1.0, right=1.1)



#    def PlotMissRateCurves(self):
#        ''' for all the cluster centers plot a miss-rate vs data size curve'''
#        file_name = "missratecurve_" + "thread_" + str(self.thread_) + ".pdf"
#        plt.figure(self.thread_ + 1)
#        F = plt.gcf()
#        default_size = F.get_size_inches()
#        F.set_size_inches((default_size[0], default_size[1]*5))
#        plt.xscale('log', basex=2)
#        plt.subplots_adjust(top=0.9)
#        x_axis = np.array([64, 256, 1024, 16384, 262144, 1048576, 2097152])
#        x_axis = np.array([64, 256, 512, 1024, 16384, 65536, 262144, 524288])
#        linesize = 64
#        i = 0
#        rows = len(self.dict_for_clustered_data_)
#        for k in self.dict_for_clustered_data_:
#            i = i + 1
#            plt.subplot(rows, 1, i)
#            y_axis = self.dict_for_clustered_data_[k].GenerateMissRateCurve(x_axis / linesize)
#            plt.plot(x_axis, y_axis)
#        plt.savefig(file_name)
#        plt.savefig(pp, format='pdf')
#        plt.close(self.thread_)   
        #pp.close()
#pylab = numpy + pyplot
        
#    def update_figure_params(self, **plot_params):
#        """Update defaults with any figure parameters given in key:param form."""
#        for k, v in plot_params.iteritems():
#            self.plot_params[k] = v
#        pl.figure(self.figure)
#        pl.rcParams.update(self.plot_params)
