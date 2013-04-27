'''
Created on Oct 27, 2011

@author: pana
'''

import math
import matplotlib.pyplot as pl
from itertools import cycle
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import sys


_inches_per_pt = 1.0 / 72.27               # Convert pt to inch
_golden_mean = (math.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
_lines = ['-', '--', '-.', ':']
_markers = ['3', 'x', '2', '+']
_linecycler = cycle(_lines)
_colors = ['r', 'b', 'g', 'c', 'm', 'y', 'k']
_patterns = ('//', '*', 'o', '\\', 'O', '.')


class Figure(object):
    
    """ Handles the plotting environment and the actual plotting for a figure. 
    
    This class acts as a wrapper around the matplotlib. Matplotlib provides
    too many options! This class restricts those choices and makes it a little 
    easier for me to handle. The figure will be plotted in one file. 
    There can be multiple sub-plots in the figure. When all plots are added, 
    the figure should be saved and closed.
    """    
    
    def __init__(self, filename, figformat='pdf', title=None, columns=1,
                 total_subplots=1, subplots_per_page=1, fig_width_pt=500.0,
                 font_size=9, title_font_size=10):
        """Initialize the plotting environment. 
        
        @param filename: file name where figure will be plotted
        @param figformat: format of figure, pdf / eps currently
        @param title: Title of the figure
        @param columns: number of columns
        @param total_subplots: total number of sub-plots in this figure
        @param subplots_per_page: subplots in 1 page, only for pdf format
        @param fig_width_pt: width of one column in pixels, 
        @param font_size: font size for everything except title
        @param title_font_size: font size for title
        
        This sets some common parameters for the figure, such as font and figure
        sizes. The size of one sub-plot is determined from the parameters. 
        The size of the figure is then set from that and the total number of 
        sub-plots.
        
        Get the column width in pixels from LaTeX using \showthe\columnwidth.

        For pdf format, we can create a multi-page file, hence we can control
        the number of subplots per page.
        
        """
        if figformat not in ('pdf', 'eps'):
            sys.stderr.write("Invalid figure format. Aborting...\n")
            sys.exit(1)
        if figformat == 'pdf':
            self.figformat = 'PDF'
            self.filename = PdfPages(filename + '.' + figformat)
            self.subplots_per_page = subplots_per_page
        else:
            self.figformat = 'PS'
            self.filename = filename + '.' + figformat
            self.subplots_per_page = total_subplots
        self.total_subplots = total_subplots
        self.num_pages = int(math.ceil(self.total_subplots /
                                         float(self.subplots_per_page)))
        self.columns = columns
        self.rows = int(math.ceil(self.subplots_per_page / 
                                        self.columns))
        self.current_plot = 0
        fig_width_in = fig_width_pt * _inches_per_pt * self.columns # width in inches
        fig_height_in = fig_width_in * _golden_mean * self.rows # height in inches
        fig_size = [fig_width_in, fig_height_in]
        self.plot_params = {'backend': self.figformat,
               'font.size': font_size,
               'axes.labelsize': font_size,
               'text.fontsize': font_size,
               'legend.fontsize': font_size,
               'xtick.labelsize': font_size,
               'ytick.labelsize': font_size,
               'text.usetex': True,
               'figure.figsize': fig_size}
        pl.rcParams.update(self.plot_params)
        self.title = title
        self.title_font_size = title_font_size
        self.create_new_figure()

    def create_new_figure(self):
        """Create a new figure"""
        self.figure = pl.figure()
        self.figure.suptitle(self.title, fontsize=self.title_font_size)

    def set_plot_param(self, subplot, xlabel=None, ylabel=None, title=None, xticks=None,
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
        if xticks:  subplot.set_xticklabels(xticks, rotation=90)

    def add_plot(self, new_style=False, labels=None, xlabel=None, ylabel=None,
                title=None, xticks=None, *args, **kwargs):
        """Add a new sub-plot to the figure.
        
        If pdf format is used savefig needs to be called for each new page.
        For eps format, savefig is called only once after all subplots are
        added.

        """
        self.current_plot += 1
        assert self.current_plot <= self.total_subplots, \
        "too many sub-plots in this figure!"
        if new_style == True: 
            kwargs['linestyle'] = next(_linecycler)
        else:
            kwargs['linestyle'] = '' #_lines[0]      # solid line by default
        kwargs['markersize'] = 4.0
        #kwargs['color'] = 'k'
        plot_id_in_page = self.current_plot % self.subplots_per_page
        if plot_id_in_page == 0: plot_id_in_page = self.subplots_per_page
        sp = self.figure.add_subplot(self.rows, self.columns, plot_id_in_page)
        lines = sp.plot(*args, **kwargs)
        sp.set_xticks(args[0])
        if labels:
            dummy = [line.set_label(label) for line, label in zip(lines, labels)]
        dummy = [line.set_marker(marker) for line, marker in zip(lines, _markers)]
        self.set_plot_param(sp, xlabel=xlabel, ylabel=ylabel, title=title, xticks=xticks, legend=True)
        new_page = ((self.current_plot % self.subplots_per_page) == 0)
        last_page = (self.current_plot == self.total_subplots)
        if new_page or last_page :
            self.figure.savefig(self.filename, format=self.figformat, bbox_inches='tight')
            self.num_pages = self.num_pages - 1
            if (self.num_pages > 0):
                self.create_new_figure()
        return sp
    
    def add_stackedbar(self, labels=None, xlabel=None, ylabel=None,
                title=None, xticks=None, *args, **kwargs):
        """Add a new stacked bar sub-plot to the figure.
        
        If pdf format is used savefig needs to be called for each new page.
        For eps format, savefig is called only once after all subplots are
        added.

        """
        self.current_plot += 1
        assert self.current_plot <= self.total_subplots, \
        "too many sub-plots in this figure!"
        kwargs['align'] = 'center'
        kwargs['linewidth'] = 0.1
        kwargs['width'] = 0.35
        colorcycler = cycle(_colors)
        patterncycler = cycle(_patterns)
        ind_axis = args[0]
        num_stacks = len(args) - 1
        plot_id_in_page = self.current_plot % self.subplots_per_page
        if plot_id_in_page == 0: plot_id_in_page = self.subplots_per_page
        sp = self.figure.add_subplot(self.rows, self.columns, plot_id_in_page)
        for i in xrange(1, num_stacks + 1):
            lower_stacks = np.sum([args[j] for j in xrange(1,i)], axis=0)
            kwargs['color'] = next(colorcycler)
            #kwargs['alpha'] = 1
            kwargs['edgecolor'] = 'black'
            #kwargs['hatch'] = next(patterncycler)
            #kwargs['bottom'] = lower_stacks
            rectangles = sp.bar(ind_axis, args[i], bottom=lower_stacks, **kwargs)
            if labels: rectangles[0].set_label(labels[i-1])
        sp.set_xticks(args[0])
        self.set_plot_param(sp, xlabel=xlabel, ylabel=ylabel, title=title, xticks=xticks, legend=True)
        new_page = ((self.current_plot % self.subplots_per_page) == 0)
        last_page = (self.current_plot == self.total_subplots)
        if new_page or last_page :
            self.figure.savefig(self.filename, format=self.figformat, bbox_inches='tight')
            self.num_pages = self.num_pages - 1
            if (self.num_pages > 0):
                self.create_new_figure()
        return sp
    
    def save_and_close(self):
        """Save & close the figure and free resources."""
        if self.figformat == 'PDF':
            self.filename.close()
        pl.close(self.figure)
         
#pl.tight_layout(pad=1.2)
#pl.subplots_adjust(bottom=0.1, top=0.9, left=1.0, right=1.1)

