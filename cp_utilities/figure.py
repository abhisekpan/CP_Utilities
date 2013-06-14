'''
Created on Oct 27, 2011

@author: pana
'''

import math
import matplotlib.pyplot as pl
from itertools import cycle
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MultipleLocator, AutoLocator
import numpy as np
import sys


_inches_per_pt = 1.0 / 72.27               # Convert pt to inch
_golden_mean = 2.0 / (math.sqrt(5) + 1.0)  # 1 / Aesthetic ratio
_lines = ['-', '--', '-.', ':']
_markers = ['3', 'x', '2', '+']
_linecycler = cycle(_lines)
_colors = ['r', 'BurlyWood', 'b', 'g', 'k', 'c', 'm', 'y']
_patterns = ('//', '*', 'o', '\\', 'O', '.')


class Figure(object):
    """
    Handles the plotting environment and the actual plotting for a figure. 
    
    This class acts as a wrapper around the matplotlib. Matplotlib provides
    too many options! This class restricts those choices and makes it a little 
    easier for me to handle. The figure will be plotted in one file. Output
    format is PDF.
    There can be multiple sub-plots in the figure. When all plots are added, 
    the figure should be saved and closed.
    """    
    
    def __init__(self, filename, title=None, columns=1,
                 total_subplots=1, subplots_per_page=1, column_width_pt=175.0,
                 font_size=6, title_font_size=6):
        """
        Initialize the plotting environment. 
        
        @param filename: file name where figure will be plotted
        @param title: Title of the figure
        @param columns: number of columns
        @param total_subplots: total number of sub-plots in this figure
        @param subplots_per_page: subplots in 1 page
        @param column_width_pt: width of one column in pixels, 
        @param font_size: font size for everything except title
        @param title_font_size: font size for title
        
        This sets some common parameters for the figure, such as font and figure
        sizes. The size of one sub-plot is determined from the parameters. 
        The size of the figure is then set from that and the total number of 
        sub-plots.
        
        Get the column width in pixels from LaTeX using \showthe\columnwidth.

        We can create a multi-page file, hence we can control the number of 
        subplots per page.
        
        """
        self.figformat = 'PDF'
        self.filename = PdfPages(filename + '.' + figformat)
        self.subplots_per_page = subplots_per_page
        self.total_subplots = total_subplots
        self.current_plot = self.current_page = 0
        #self.num_pages = int(math.ceil(self.total_subplots /
        #    float(self.subplots_per_page)))
        self.columns = columns
        self.rows = int(math.ceil(self.subplots_per_page / self.columns))
        fig_width_in = column_width_pt * _inches_per_pt * self.columns 
        fig_height_in = fig_width_in * _golden_mean * self.rows 
        fig_size = [fig_width_in, fig_height_in]
        self.plot_params = {'backend': self.figformat,
               'font.size': font_size,
               'axes.labelsize': font_size,
               'legend.fontsize': font_size,
               'legend.labelspacing': 0.05,
               'xtick.labelsize': font_size,
               'ytick.labelsize': font_size,
               'text.usetex': True,
               'figure.figsize': fig_size}
        pl.rcParams.update(self.plot_params)
        self.title = title
        self.title_font_size = title_font_size

    def create_new_figure(self, print_title=False):
        """
        Create a new figure.
        
        Title is printed only for the first page. Hence the flag.

        """
        self.figure = pl.figure()
        if (print_title == True) and (self.title is not None):
            self.figure.suptitle(self.title, fontsize=self.title_font_size)

    def handle_page_break(self):
        """
        Handle page breaks based on the number of subplots added.
        Save the figure at the end of each page. Create a new figure
        at the start of each page.
        Return plot id in page.

        """
        assert self.current_plot < self.total_subplots, \
        "too many sub-plots in this figure!"
        plot_id_in_page = (self.current_plot % self.subplots_per_page) + 1
        new_page = (plot_id_in_page == 1)
        if new_page:
            if self.current_page == 0:
                self.create_new_figure(print_title=True)
            else:
                self.figure.savefig(self.filename, format=self.figformat,
                                    bbox_inches='tight')
                self.create_new_figure()
            self.current_page += 1
        self.current_plot += 1
        return plot_id_in_page

    def set_legend_format(self, sp, legend_loc=0, legend_ncol=1,
                          bbox_to_anchor=None, **kwargs):
        """
        Format legend for a subplot.

        @param sp: the subplot for which legends are set 
        @param legend_loc: location of the legend.
        @param legend_ncol: number of columns in the legend.
        @param bbox_to_anchor: specfy legend loc in normalized co-ordinates
        @param **kwargs: any other relevant parameters

        The location codes for legend are
        Location String 	Location Code
        'best'          0
    	'upper right'	1
    	'upper left'	2
    	'lower left'	3
    	'lower right'	4
    	'right'  	5
    	'center left'	6
    	'center right'	7
    	'lower center'	8
    	'upper center'	9
    	'center'	10

        bbox_to_anchor is used to specify any arbitrary location for the legend.
        For example,
        loc = 'upper right', bbox_to_anchor = (0.5, 0.5)
        will place the legend so that the upper right corner of the legend at
        the center of the axes.
        
        """
        sp.legend(loc=legend_loc, ncol=legend_ncol,
                       bbox_to_anchor=bbox_to_anchor, **kwargs)
    
    def set_axis_format(self, sp, axis, label=None, ticks=None, limits=None, 
                        tick_labels=None, scientific=False):
        """
        Set parameters for an axis.

        @param sp: the subplot for which parameters are set 
        @param axis: the axis to format: x, y
        @param label: label for axis
        @param: ticks: list of ticks
        @param: limits: data limits for axis (min, max)
        @param: tick_labels: labels for individual ticks
        @param: scientific: scientific notation for tick labels
       
        Notes about axis modifiers:
        Formatter:
        Formatter determines how ticks locations are converted into strings.
        Interesting formatters:
        FixedFormatter: sets the strings manually for the lables
        FuncFormatter: user-defined functions set the labels
        FormatStrFormatter: use a spritf format string
        ScalarFormatter: tick is a plain old number, default for scalars
        LogFormatter: Formatter for log axes
        
        ticklabel_format is a convenience wrapper function that sets the ticks
        in scientific format by calling the methods of the axes Formatter.
        Works only with ScalarFormatter (defualt). For example,
        subplot.ticklabel_format(style='sci',scilimits=(-3,4),axis='both')
        can be replaced by the following for each of the axes:
        subplot.get_xaxis().get_major_formatter().set_scientific(True)
        subplot.get_xaxis().get_major_formatter().set_powerlimits((-3,4))

        set_xticklabels is a convinience wrapper function that uses the 
        FixedFormatter to set the labels of xticks with the labels passed.

        Locator:
        Locator handles auto-scaling of tick limits based on data limits and
        choosing of tick locations. Interesting locators:
        FixedLocator: Tick Locations are fixed
        IndexLocator: Locator for index plots (eg. where x = range(len(y)))
        LinearLocator: Evenly spaced ticks from min to max
        LogLocator: Logarithmically ticks from min to max
        MultipleLocator: Ticks and range on multiples of bases
        AutoLocator: A maximum number of ticks at nice locations
        For example:
        subplot.xaxis.set_major_locator( MultipleLocator(1.00) )
        subplot.yaxis.set_major_locator( AutoLocator )

        set_ticks_position determines if the ticks will be visibile on both
        sides of data (bottom and top axes for x-axis) or just one side.
    
        Additional commands that might be helpful:
        set the space between the axes and the end of fig  -
        [left, bottom, width, height] in normalized (0, 1) units.
        subplot.set_position([0.1, 0.15, 0.8, 0.7]) 

        """
        assert axis in ['x', 'y'], "axis has to be x or y"
        if axis == 'x':
            sp.xaxis.set_ticks_position('bottom')
            if label: sp.set_xlabel(r'\textit{' + label + '}')
            if ticks: sp.set_xticks(ticks)
            if limits: sp.set_xlim([0,1])
            if tick_labels: sp.set_xticklabels(tick_labels, rotation=70)
            if scientific:
                subplot.ticklabel_format(style='sci',scilimits=(-3,4),axis='x')
        else:
            sp.yaxis.set_ticks_position('left')
            if label: sp.set_ylabel(r'\textit{' + label + '}')
            if ticks: sp.set_yticks(ticks)
            if limits: sp.set_ylim([0,1])
            if tick_labels: sp.set_yticklabels(tick_labels, rotation=70)
            if scientific:
                subplot.ticklabel_format(style='sci',scilimits=(-3,4),axis='y')
    
    def set_subplot_title(self, sp, title):
        """
        Set subplot title.

        @param sp: the subplot for which parameters are set 
        @param title: title of the subfigure using this axis

        """
        sp.set_title(title.encode('string-escape'))
    
    def set_spine_format(self, sp):
        """
        Set the format of the spines, which are the axes lines that join
        the ticks.

        They can be positioned with respect to the axes or data limits
        (used here). Smart Bounds - Spines  attempt to set bounds in a 
        sophisticated way.
        """
        for direction in ['left','bottom']:
            sp.spines[direction].set_position(('data', -1.0))
            sp.spines[direction].set_smart_bounds(True)
        for direction in ['right','top']:
            sp.spines[direction].set_color('none')

    def add_plot(self, line_plot=False, new_style=False, labels=None,
                 xlabel=None, ylabel=None, title=None, xtick_labels=None,
                 legend=True, *args, **kwargs):
        """
        Add a new sub-plot to the figure.

        """
        if line_plot == True:
            if new_style == True: kwargs['linestyle'] = next(_linecycler)
            else: kwargs['linestyle'] = lines[0]  # Solid line by default.
        else:
                kwargs['linestyle'] = '' # No lines, only points.
        kwargs['markersize'] = 4.0
        plot_id_in_page = self.handle_page_break()
        sp = self.figure.add_subplot(self.rows, self.columns, plot_id_in_page)
        lines = sp.plot(*args, **kwargs)
        if labels:
            dummy = [line.set_label(label) for line, label in zip(lines, labels)]
        dummy = [line.set_marker(marker) for line, marker in zip(lines, _markers)]
        self.set_axis_format(sp, 'x', label=xlabel, ticks=args[0],
                             tick_labels=xtick_labels)
        self.set_axis_format(sp, 'y', label=ylabel, limits=[0,1])
        if title: self.set_subplot_title(title)
        if legend: self.set_legend_format(sp)
        return sp
    
    def add_stackedbar(self, labels=None, xlabel=None, ylabel=None,
                title=None, xtick_labels=None, legend=True, *args, **kwargs):
        """
        Add a new stacked bar sub-plot to the figure.

        """
        kwargs['align'] = 'center'
        kwargs['linewidth'] = 0.1
        kwargs['width'] = 0.35
        colorcycler = cycle(_colors)
        patterncycler = cycle(_patterns)
        ind_axis = args[0]
        num_stacks = len(args) - 1
        plot_id_in_page = self.handle_page_break()
        sp = self.figure.add_subplot(self.rows, self.columns, plot_id_in_page)
        for i in xrange(1, num_stacks + 1):
            lower_stacks = np.sum([args[j] for j in xrange(1,i)], axis=0)
            kwargs['color'] = next(colorcycler)
            kwargs['edgecolor'] = 'black'
            rectangles = sp.bar(ind_axis, args[i], bottom=lower_stacks, **kwargs)
            if labels: rectangles[0].set_label(labels[i-1])
        self.set_spine_format(sp)
        self.set_axis_format(sp, 'x', label=xlabel, ticks=args[0],
                             tick_labels=xtick_labels)
        self.set_axis_format(sp, 'y', label=ylabel)
        if title: self.set_subplot_title(title)
        if legend: self.set_legend_format(sp)
        return sp
    
    def save_and_close(self):
        """Save & close the figure and free resources."""
        self.figure.savefig(self.filename, format=self.figformat, 
                            bbox_inches='tight')
        self.filename.close()
        pl.close(self.figure)
         
