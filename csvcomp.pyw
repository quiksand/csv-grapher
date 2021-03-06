###############################################################################
#                   CSV Graphing Utility
# This little script will generate a graph of all the csv files in the CWD.
# Graphs can be added, removed, exported, and tweaked in various ways.
# Please see the documentation for more information.
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
###############################################################################

import csv
import argparse
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import cursors
import matplotlib.backends.backend_tkagg as tkagg
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import xlsxwriter as xw

class SnaptoCursor(object):
    """
    Cursor object that tracks series data on plot.
    """
    cursors = {}
    #TODO: Give an optional initial x state coord
    def __init__(self, master, ax_num, series=None):
        self.master = master
        self.ax_num = ax_num
        self.axes = self.master.fig.axes
        self.series = series
        self.x = np.array(series.x)
        self.y = np.array(series.y)
        self.vert_line = self.axes[self.ax_num].axvline(color='k', picker=1)  # the vert line
        x_start = self.x[series.peak_index]
        y_start = self.y[series.peak_index]
        self.last_event_x = x_start
        self.data_point = self.axes[self.ax_num].plot([x_start],
                                            [y_start],
                                            marker='o',
                                            markersize=5,
                                            markerfacecolor = 'none',
                                            color='k')[0]
        self.vert_line.set_xdata(x_start)
        self.text = self.axes[self.ax_num].text(x_start,
                                            y_start,
                                            '({:.3f}, {:.3e})'.format(x_start, y_start))
        # SnaptoCursor.cursors[self.series.label] = self
        SnaptoCursor.cursors[self.ax_num] = self
    def mouse_move(self, event):
        #mostly just returns if events are's just right
        if not event.inaxes:
            return
        if event.button != 1:
            return
        if event.inaxes != self.axes[self.ax_num]:
            return
        if not self.data_point.get_visible():
            return
        self.last_event_x = event.xdata
        self.update_position()
    def update_position(self):
        #the real meat and potatoes. updates cursor drawing.
        index = np.searchsorted(self.x, [self.last_event_x])[0]
        x = self.x[index]
        y = self.y[index]
        self.data_point.set_xdata(x)
        self.data_point.set_ydata(y)
        self.vert_line.set_xdata(x)
        s = '({:.3f}, {:.3e})'.format(x, y)
        self.text.set_x(x)
        self.text.set_y(y)
        self.text.set_text(s)
        self.master.canvas.show()
    def hide(self):
        self.data_point.set_visible(False)
        self.vert_line.set_visible(False)
        self.text.set_visible(False)
        self.master.canvas.show()
    def show(self):
        self.data_point.set_visible(True)
        self.vert_line.set_visible(True)
        self.text.set_visible(True)
        self.master.canvas.show()
    def update_series(self, series=None):
        self.series = series
        if self.series == None:
            if not Series.obj_list:
                print('Nothing to put a cursor on')
                self.hide()
                del self
                return
            for key in Series.obj_list.keys():
                self.master.radio_var.set(key)
                self.series = Series.obj_list[key]
                break
        self.x = np.array(self.series.x)
        self.y = np.array(self.series.y)
        self.update_position()
    def update_axes(self):
        self.axes = self.master.fig.axes

#TODO Rearrange widgets to make more sense in layout
class GUI(tk.Frame):
    """Main GUI Window
    Basically a giant container for everything on the screen.
    This class is a tad bloated. A redesign is encouraged.
    """
    gui = None
    def __init__(self, master):
        #TODO: Abstract this out to somewhere
        #argument parsing
        parser = argparse.ArgumentParser(description='Plots one or more .csv files')
        parser.add_argument('-f', dest='f', required=False,
            help='Specify path to a csv file to graph')
        parser.add_argument('-d', dest='dir', default='./', required=False,
            help='Specify a directory of csv files to graph')
        parser.add_argument('-o', dest='of', default='../CombinedCSV.csv', required=False,
            help='Specify an output filename to condense all csv files into one')
        args = parser.parse_args()
        #procedure if file is specified
        if args.f:
            csv_path = os.path.abspath(args.f)
            if not check_path(csv_path):
                print("Error: File path does not exist or is not correct format")
                return 1
            self.read_in_csv(csv_path)

        #procedure if directory is given or file not specified
        else:
            for f in os.listdir(args.dir):
                csv_path = os.path.abspath(os.path.join(args.dir, f))
                if check_path(csv_path):
                    # Series(csv_path)
                    self.read_in_csv(csv_path)

        tk.Frame.__init__(self, master)
        master.title("CSV Grapher")
        master.protocol('WM_DELETE_WINDOW', self._quit)
        self.fig = plt.figure()
        self.no_of_subplots = 1
        self.subplot_layouts = [[111],[211,212],[211,223,224],[221,222,223,224]]
        self.subplots = [None]*self.no_of_subplots
        self.default_x_label = tk.StringVar()
        self.default_x_label.set('Frequency (kHz)')
        self.default_y_label = tk.StringVar()
        self.default_y_label.set('Amplitude (V)')
        self.xlabel = [self.default_x_label.get()]*4
        self.ylabel = [self.default_y_label.get()]*4
        self.testvar=tk.DoubleVar()
        self.radio_var = tk.StringVar()
        #set radio_var to first series in dict of series. Probs a better way.
        for key in Series.obj_list.keys():
            self.radio_var.set(key)
            break

        self.plot_controls_frame = tk.Frame(self, bg="black", bd=1)
        self.graph_frame = tk.Frame(self)
        self.toolbar_frame = tk.Frame(self)
        self.legend_list_frame = tk.Frame(self, bg="black", bd=1)
        self.export_button_frame = tk.Frame(self, bg="black", bd=1)

        self.open_button = ttk.Button(self,
                                    text="Add file",
                                    command=self.load_file)
        self.export_csv_button = ttk.Button(self.export_button_frame,
                                    text='Export CSV',
                                    command=self.export_csv)
        self.export_excel_button = ttk.Button(self.export_button_frame,
                                    text='Export to Excel',
                                    command=self.export_excel)
        self.add_plot_button = ttk.Button(self,
                                    text="Add plot",
                                    command=self.add_a_subplot)
        self.remove_plot_button = ttk.Button(self,
                                    text="Remove Plot",
                                    command=self.remove_a_subplot)
        self.rescale_button = ttk.Button(self.export_button_frame,
                                    text='Rescale All Series',
                                    command=self.rescale_all)
        # self.test_button = ttk.Button(self.export_button_frame,
        #                             text='Test Button',
        #                             command=self.todo5)
        # self.test_button_2 = ttk.Button(self.export_button_frame,
        #                             text='Test Button 2',
        #                             command=self.todo4)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.header_bar = Series_Control_Row_Title_Bar(self.legend_list_frame)

        self.adjust_subplots()

        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        self.open_button.grid(row=5, column=5)
        self.export_csv_button.grid(sticky=tk.E+tk.W)
        self.export_excel_button.grid(sticky=tk.E+tk.W)
        self.rescale_button.grid(sticky=tk.E+tk.W)
        # self.test_button.grid(sticky=tk.E+tk.W)
        # self.test_button_2.grid(sticky=tk.E+tk.W)
        self.graph_frame.grid(row=0, column=0, columnspan=5, rowspan=5, sticky=tk.N+tk.E+tk.W+tk.S)
        self.legend_list_frame.grid(row=1, column=5, rowspan=4, padx=10, pady=10, sticky=tk.N+tk.S)
        self.export_button_frame.grid(row=6, column=5)
        self.plot_controls_frame.grid(row=5, column=0, columnspan=5)
        self.add_plot_button.grid(row=6, column=2)
        self.remove_plot_button.grid(row=6, column=3)
        self.toolbar_frame.grid(row=7, column=0, columnspan=5, sticky=tk.W)
        GUI.gui = self

#DELETE########################################################################
    def todo4(self):
        exceltest.testfunc([series for series in Series.obj_list.values()])
    def todo5(self):
        self.open_excel_export_window()
#/DELETE#######################################################################

    def rescale_all(self):
        if Edit_Series_Window.no_instance:
            Edit_Series_Window(self)
    def open_excel_export_window(self):
        if Excel_Export_Window.no_instance:
            Excel_Export_Window(self)
    def read_in_csv(self, path_to_csv):
        rows = []
        cols = []
        new_series = []
        with open(path_to_csv, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                rows.append(row)
        for i in range(len(rows[0])):
            cols.append([col[i] for col in rows])
        if len(cols) < 2:
            print('ERROR - Nothing to graph in csv')
            return new_series
        for i in range(1,len(cols)):
            label = os.path.split(path_to_csv)[1].lower()[:-4]
            if len(cols) > 2:
                label = label + ' - Series {}'.format(i)
            new_series.append(Series(cols[0], cols[i], path_to_csv, label))
        return new_series
    def plot_series(self, series, axes=None):
        # series.axes_index = []
        if axes != None:
            #Put code here to accept axes? Maybe take subplot index instead?
            print('PLOTTING')
            return
        series.artists = []
        for ax in self.fig.axes:
            if series.plot_type == 'scatter':
                art = ax.scatter(series.x, series.y, label=series.label, picker=1)
            else:
                [art] = ax.plot(series.x, series.y, label=series.label, picker=1)
            series.artists.append(art)
        #FIXME: legend sometimes causes a warning to be issued.
        self.legend = plt.legend()
        self.canvas.show()
        for artist in series.artists:
            artist.set_visible(series.show)
        if series.label not in Series_Control_Row.control_rows.keys():
            Series_Control_Row(self.legend_list_frame, series)
        self.canvas.show()
    def plot_multiple_series(self, axes=None):
        for series in Series.obj_list.values():
            self.plot_series(series, axes)
    def insert_plot_control(self, index):
        Plot_Control_Row(self.plot_controls_frame, index)
    def plot_cursors(self):
        self.cursor = [None]*self.no_of_subplots
        self.cid = [None]*self.no_of_subplots
        cursor_series = self.radio_var.get()
        if cursor_series == '':
            return
        for i in range(self.no_of_subplots):
            self.cursor[i] = SnaptoCursor(
                                        self,
                                        i,
                                        Series.obj_list[cursor_series])
            self.cid[i] = self.canvas.mpl_connect(
                                        'motion_notify_event',
                                        self.cursor[i].mouse_move)
        self.header_bar.header.show_or_hide_cursors()
    def adjust_subplots(self):
        self.fig.clear()
        for i, j in enumerate(self.subplot_layouts[self.no_of_subplots-1]):
            self.subplots[i] = self.fig.add_subplot(j)
            if i not in Plot_Control_Row.plot_control_rows.keys():
                self.insert_plot_control(i)
            self.subplots[i].set_xlabel(self.xlabel[i])
            self.subplots[i].set_ylabel(self.ylabel[i])
            self.subplots[i].grid(Plot_Control_Row.plot_control_rows[i].grid_var.get())
        self.plot_multiple_series()
        self.plot_cursors()
        self.fig.tight_layout()
        self.canvas.show()
    def add_a_subplot(self):
        if self.no_of_subplots < 4:
            self.no_of_subplots += 1
            self.subplots.append(None)
        self.adjust_subplots()
    def remove_a_subplot(self):
        if self.no_of_subplots > 1:
            del self.subplots[-1]
            Plot_Control_Row.plot_control_rows[self.no_of_subplots-1].destroy()
            del Plot_Control_Row.plot_control_rows[self.no_of_subplots-1]
            del SnaptoCursor.cursors[self.no_of_subplots-1]
            self.no_of_subplots -= 1
        self.adjust_subplots()
    def _quit(self):
        self.master.quit()
        self.master.destroy()
    def export_csv(self):
        #TODO: Simplify, possibly remove extra call to write_csv
        #TODO: Grey out button if no plots are in Series.obj_list
        fname = tk.filedialog.asksaveasfilename(filetypes=(("csv", "*.csv"),
            ("All files", "*.*") ), defaultextension=".csv", initialfile="CombinedCSV.csv")
        if fname:
            self.write_csv(fname)
    def write_csv(self, of):
        #TODO: Simplify.
        labels = [GUI.gui.xlabel[0]]
        xs = []
        ys = []
        rows = []
        for series in Series.obj_list.values():
            if series.show:
                labels.append(series.label)
                xs.append(series.x)
                ys.append(series.y)
        rows.append(labels)
        for index, val in enumerate(xs[0], start = 0):
            rows.append([])
            rows[index+1].append(xs[0][index])
            for y in ys:
                rows[index+1].append(y[index])
        with open(of, 'w', newline='') as newcsv:
            writer = csv.writer(newcsv)
            writer.writerows(rows)
    def export_excel(self):
        fname = tk.filedialog.asksaveasfilename(filetypes=(("xlsx", "*.xlsx"),
            ("All files", "*.*") ), defaultextension=".xlsx", initialfile="CombinedXlsx.xlsx")
        if fname:
            self.write_xlsx(fname)
    def write_xlsx(self, of):
        export_list = []
        for series in Series.obj_list.values():
            if series.show:
                export_list.append(series)
        self.churn_out_excel(export_list, of)
    def churn_out_excel(self, series_list, of, options={'graph':True}):
        '''Takes a list of series and writes them to excel workbook'''
        workbook = xw.Workbook(of)
        worksheet = workbook.add_worksheet()
        if options['graph']:
            # for plot in plots:
            # for i in range(number_of_charts):
            chart = workbook.add_chart({'type': 'scatter', 'subtype':'straight'})
        row = 0
        col = 0
        for series in series_list:
            row = 0
            worksheet.write(row, col, series.label + ' X')
            row += 1
            worksheet.write_column(row, col, series.x)
            row = 0
            col += 1
            worksheet.write(row, col, series.label)
            row += 1
            worksheet.write_column(row, col, series.y)
            if options['graph']:
                # for plot in plots
                self.add_series_to_chart(series, col, chart)
            col += 1
        if options['graph']:
            # for plot in plots
            worksheet.insert_chart('B7', chart, {'x_scale': 2.5, 'y_scale': 2})
            self.add_chart_props(chart)
        # graph_excel(workbook, worksheet)
        workbook.close()
        print('Created Excel workbook: {}'.format(of))
    def add_series_to_chart(self, series, col, chart):
        chart.add_series({
                            'name': ['Sheet1', 0, col, 0, col],
                            'categories': ['Sheet1', 1, col-1, len(series.x), col-1],
                            'values': ['Sheet1', 1, col, len(series.x), col]
                            })
    def add_chart_props(self, chart):
        chart.set_legend({
            'position': 'overlay_right',
            'font': {'size': 12}
            })
        chart.set_title({
            'name': 'CHANGEME',
            'name_font': {'bold': False, 'size': 14}
            })
        chart.set_y_axis({
            'name': GUI.gui.ylabel[0],
            'major_gridlines': {'visible': True},
            'name_font': {'bold': False, 'size': 12}
            })
        chart.set_x_axis({
            'name': GUI.gui.xlabel[0],
            'major_gridlines': {'visible': True},
            'name_font': {'bold': False, 'size': 12},
            'max': 2.0
            })
    #TODO: Make this logic better
    def load_file(self):
        f_names = tk.filedialog.askopenfilename(filetypes=(("Csv files", "*.csv"),
            ("All files", "*.*")), multiple=True, )
        if f_names:
            # self.open_button.pack_forget()
            for each_file in f_names:
                new_series = self.read_in_csv(each_file)
                for series in new_series:
                    self.plot_series(series)

class Excel_Series_Options_Row(tk.Frame):
    rows = {}
    def __init__(self, master, row):
        tk.Frame.__init__(self, master)
        self.series = row.series
        self.series_label = ttk.Label(self,
                                    text=self.series.label)
        self.subplot_check_boxes = []
        for i in range(GUI.gui.no_of_subplots):
            subplot_check_box = ttk.Checkbutton(self,
                                                text='Plot {}:'.format(i+1),
                                                command=todo)
            subplot_check_box.pack(side=tk.LEFT)
            self.subplot_check_boxes.append(subplot_check_box)
        self.grid()
        Excel_Series_Options_Row.rows[self.series.label] = self

class Excel_Export_Window(tk.Toplevel):
    no_instance = True
    def __init__(self, master):
        Excel_Export_Window.no_instance = False
        tk.Toplevel.__init__(self, master)
        self.title('Export to Excel')
        # self.blah = ttk.Label(master=self, text='Put something Here!!')
        # self.blah.gri(fill=tk.BOTH, expand=1)
        self.series_options_frame = ttk.Frame(self)
        # self.plot_options_frame = tk.Frame(self, bg="black", bd=1)
        print(Series_Control_Row.control_rows.values())
        print(len(Series_Control_Row.control_rows))
        for row in Series_Control_Row.control_rows.values():
            Excel_Series_Options_Row(self.series_options_frame, row)
        self.series_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N+tk.S)
        # self.plot_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N+tk.S)

    def __del__(self):
        Excel_Export_Window.no_instance = True
    def todo(self):
        print('TODO')

    def get_plot_options(self):
        self.todo()
        # list or dict of "plots"
        #each plot should have:
            #grid on each plots true or False
            # list of series to graph
            #x and y min/max
            # axis titles
            #series type?
            #possibly need to call graph reverse if excel doesn't do that automatically

    def get_series_options(self):
        self.todo()

    #main excel writing function
    def write_series_to_excel(self, series_list, options={'graph':True}):
        '''Takes a list of series and writes them to excel workbook'''
        workbook = xw.Workbook('combined.xlsx')
        worksheet = workbook.add_worksheet()
        if options['graph']:
            # for plot in plots:
            # for i in range(number_of_charts):
            chart = workbook.add_chart({'type': 'scatter', 'subtype':'straight'})
        row = 0
        col = 0
        for series in series_list:
            row = 0
            worksheet.write(row, col, series.label + ' X')
            row += 1
            worksheet.write_column(row, col, series.x)
            row = 0
            col += 1
            worksheet.write(row, col, series.label)
            row += 1
            worksheet.write_column(row, col, series.y)
            if options['graph']:
                # for plot in plots
                add_series_to_chart(series, col, chart)
            col += 1
        if options['graph']:
            # for plot in plots
            worksheet.insert_chart('A7', chart)
        # graph_excel(workbook, worksheet)
        workbook.close()
        print('Created Excel workbook')

    def add_series_to_chart(series, col, chart):
        chart.add_series({
                            'name': ['Sheet1', 0, col, 0, col],
                            'categories': ['Sheet1', 1, col-1, len(series.x), col-1],
                            'values': ['Sheet1', 1, col, len(series.x), col]
                            })

class Plot_Control_Row(GUI):
    plot_control_rows = {}
    def __init__(self, master, subplot_index):
        tk.Frame.__init__(self, master)
        self.configure(bd=1)
        self.subplot_index = subplot_index
        self.label = 'Plot {}'.format(self.subplot_index+1)
        self.grid_var = tk.BooleanVar()
        self.grid_var.set(0)
        self.x_lower_bound = tk.DoubleVar()
        self.x_lower_bound.set(0)
        self.x_upper_bound = tk.DoubleVar()
        self.x_upper_bound.set(1)
        self.xbar = tk.DoubleVar()
        self.y_lower_bound = tk.DoubleVar()
        self.y_lower_bound.set(0)
        self.y_upper_bound = tk.DoubleVar()
        self.y_upper_bound.set(0.004)
        self.ybar = tk.DoubleVar()

        # Row Label
        self.plot_label = ttk.Label(self,
                                    text = self.label + ': ',
                                    anchor = tk.W)
        # X Controls
        self.x_scale_label = ttk.Label(self,
                                    text = 'X: ',
                                    width = 3,
                                    anchor = tk.E)
        self.x_scale_box_lower = ttk.Entry(self,
                                    width = 5,
                                    textvariable = self.x_lower_bound)
        self.x_scale_slider = ttk.Scale(self,
                                    length = 100,
                                    from_ = 0.001,
                                    var = self.xbar,
                                    command = self.x_slider_moved)
        self.x_scale_box_upper = ttk.Entry(self,
                                    width = 5,
                                    textvariable = self.x_upper_bound)
        # Y Controls
        self.y_scale_label = ttk.Label(self,
                                    text = 'Y: ',
                                    width = 3,
                                    anchor = tk.E)
        self.y_scale_box_lower = ttk.Entry(self,
                                    width = 5,
                                    textvariable = self.y_lower_bound)
        self.y_scale_slider = ttk.Scale(self,
                                    length = 100,
                                    from_ = 0.001,
                                    var = self.ybar,
                                    command = self.y_slider_moved)
        self.y_scale_box_upper = ttk.Entry(self,
                                    width = 5,
                                    textvariable = self.y_upper_bound)
        # Grid Checkbox
        self.grid_checkbox = ttk.Checkbutton(self,
                                    variable=self.grid_var,
                                    text='Grid',
                                    command=self.show_or_hide_grid)
        # Edit Button
        self.edit_plot_button = ttk.Button(self,
                                    text="...",
                                    width = 3,
                                    command = self.open_edit_plot_window)
        # Resize Button
        # self.resize_button = ttk.Button(self,
        #                             text = 'Rescale',
        #                             command = self.update_bounds)
        #Reset button
        # self.reset_button = ttk.Button(self,
        #                             text = 'Reset',
        #                             command = self.reset_bounds)
        #Key Bindings
        self.x_scale_box_lower.bind('<Return>', self.update_x_bounds)
        self.x_scale_box_upper.bind('<Return>', self.update_x_bounds)
        self.y_scale_box_lower.bind('<Return>', self.update_y_bounds)
        self.y_scale_box_upper.bind('<Return>', self.update_y_bounds)
        self.grid_checkbox.bind('<Return>', self.show_or_hide_grid)
        # self.reset_button.bind('<Return>', self.reset_bounds)

        # Packing
        self.plot_label.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.x_scale_label.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.x_scale_label.grid(row=0, column=2, sticky=tk.N+tk.S)
        self.x_scale_box_lower.grid(row=0, column=3, sticky=tk.N+tk.S)
        self.x_scale_box_lower.grid(row=0, column=4, sticky=tk.N+tk.S)
        self.x_scale_slider.grid(row=0, column=5, sticky=tk.N+tk.S)
        self.x_scale_box_upper.grid(row=0, column=6, sticky=tk.N+tk.S)
        self.x_scale_box_upper.grid(row=0, column=7, sticky=tk.N+tk.S)
        self.y_scale_label.grid(row=0, column=8, sticky=tk.N+tk.S)
        self.y_scale_box_lower.grid(row=0, column=9, sticky=tk.N+tk.S)
        self.y_scale_slider.grid(row=0, column=10, sticky=tk.N+tk.S)
        self.y_scale_box_upper.grid(row=0, column=11, sticky=tk.N+tk.S)
        self.grid_checkbox.grid(row=0, column=12, sticky=tk.N+tk.S)
        self.edit_plot_button.grid(row=0, column=13, sticky=tk.N+tk.S)
        # self.resize_button.grid(row=0, column=13, sticky=tk.N+tk.S)
        # self.reset_button.grid(row=0, column=13, sticky=tk.N+tk.S)
        self.grid(sticky=tk.E+tk.W)

        Plot_Control_Row.plot_control_rows[self.subplot_index] = self

    def todo2(self, val):
        print(val)
    #TODO: Put some validation code in for the boxes
    #TODO: Rethink the way the slider scales
    # def update_axes(self, axes):
    #     self.axes = axes
    def open_edit_plot_window(self):
        if Edit_Plot_Window.no_instance:
            Edit_Plot_Window(self, self.subplot_index)
    def show_or_hide_grid(self, event=None):
        if event:
            self.grid_var.set(not self.grid_var.get())
        self.master.master.subplots[self.subplot_index].grid(self.grid_var.get())
        self.master.master.canvas.show()
    def rescale_x_axes(self, a, b):
        self.master.master.subplots[self.subplot_index].set_xlim(a, b)
        # self.axes.set_xlim(a, b)
        self.master.master.canvas.show()
    def rescale_y_axes(self, a, b):
        self.master.master.subplots[self.subplot_index].set_ylim(a, b)
        # self.axes.set_ylim(a, b)
        self.master.master.canvas.show()
    def update_x_bounds(self, event=None):
        self.rescale_x_axes(self.x_lower_bound.get(), self.x_upper_bound.get())
        if event != None:
            self.x_scale_slider.set(100)
    def update_y_bounds(self, event=None):
        self.rescale_y_axes(self.y_lower_bound.get(), self.y_upper_bound.get())
        if event != None:
            self.y_scale_slider.set(100)
    def reset_bounds(self, event=None):
        self.master.master.subplots[self.subplot_index].clear()
        # self.master.master.subplots[self.subplot_index]
        self.grid_var.set(0)
        self.master.master.subplots[self.subplot_index].set_xlabel(self.master.master.xlabel[self.subplot_index])
        self.master.master.subplots[self.subplot_index].set_ylabel(self.master.master.ylabel[self.subplot_index])
        self.master.master.subplots[self.subplot_index].grid(self.grid_var.get())
        # self.master.master.plot_multiple_series() #Edit to take an axes arg. Lotta work...
        # self.master.master.plot_cursors()
        # self.fig.tight_layout()
        self.master.master.canvas.show()
    def x_slider_moved(self, val):
        a = self.x_lower_bound.get()
        b = self.x_upper_bound.get()
        x = self.xbar.get()
        b = a+x*(b-a)
        self.rescale_x_axes(a, b)
    def y_slider_moved(self, val):
        a = self.y_lower_bound.get()
        b = self.y_upper_bound.get()
        y = self.ybar.get()
        b = a+y*(b-a)
        self.rescale_y_axes(a, b)

class Edit_Plot_Window(tk.Toplevel):
    """Edit Plot Window is accessed via the '...' button in the plot control row.
    This window provides extra options for altering plot data and display.
    Only one window may be open at any given time.
    Currently only axes name changes are allowed from this window.
    """
    no_instance = True
    def __init__(self, master, index):
        Edit_Series_Window.no_instance = False
        self.index = index
        tk.Toplevel.__init__(self, master)
        self.x_label = tk.StringVar()
        self.x_label.set(GUI.gui.xlabel[self.index])
        self.y_label = tk.StringVar()
        self.y_label.set(GUI.gui.ylabel[self.index])
        self.title('Edit Plot')
        self.protocol('WM_DELETE_WINDOW', self._quit)
        self.lab_x = ttk.Label(master=self, text='X Axis Label')
        self.lab_y = ttk.Label(master=self, text='Y Axis Label')
        self.x_axis_label_entry = ttk.Entry(self, textvariable=self.x_label)
        self.y_axis_label_entry = ttk.Entry(self, textvariable=self.y_label)
        self.update_btn = ttk.Button(self,
                                    text = 'Update Axes Labels',
                                    command = self.update)
        self.lab_x.pack(fill=tk.BOTH, expand=1)
        self.x_axis_label_entry.pack(fill=tk.BOTH, expand=1)
        self.lab_y.pack(fill=tk.BOTH, expand=1)
        self.y_axis_label_entry.pack(fill=tk.BOTH, expand=1)
        self.update_btn.pack(fill=tk.BOTH, expand=1)
        self.bind('<Return>', self.update)
    def _quit(self):
        Edit_Series_Window.no_instance = True
        self.destroy()
    def update(self, event=None):
        #This should be a GUI method, but there's a lot that should be different in this program...
        GUI.gui.subplots[self.index].set_xlabel(self.x_label.get())
        GUI.gui.xlabel[self.index] = self.x_label.get()
        GUI.gui.subplots[self.index].set_ylabel(self.y_label.get())
        GUI.gui.ylabel[self.index] = self.y_label.get()
        GUI.gui.adjust_subplots()
        self._quit()

class Series_Control_Row_Title_Bar(GUI):
    """It's just a title bar for the list of series control rows."""
    header = None
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        # self.config(bg="black", bd=1)
        self.cursor_var = tk.BooleanVar()
        self.cursor_var.set(1)
        self.checkvar2 = tk.BooleanVar()
        self.checkvar2.set(1)
        self.cursor_checkbox = ttk.Checkbutton(self,
                                    variable = self.cursor_var,
                                    command = self.show_or_hide_cursors)
        self.show_hide_checkbox = ttk.Checkbutton(self,
                                    variable = self.checkvar2,
                                    command = self.show_or_hide_all)
        self.series_header_label = ttk.Label(self,
                                    anchor = tk.CENTER,
                                    text = 'Series',
                                    width = 40)
        self.series_edit_label = ttk.Label(self,
                                    anchor = tk.CENTER,
                                    width = 5,
                                    text = 'Edit')
        self.series_remove_label = ttk.Label(self,
                                    anchor = tk.CENTER,
                                    width = 11,
                                    text = 'Remove')
        self.cursor_checkbox.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.show_hide_checkbox.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.series_header_label.grid(row=0, column=2, sticky=tk.N+tk.S)
        self.series_edit_label.grid(row=0, column=3, sticky=tk.N+tk.S)
        self.series_remove_label.grid(row=0, column=4, sticky=tk.N+tk.S)
        self.grid(sticky=tk.W+tk.E)
        Series_Control_Row_Title_Bar.header = self
    def show_or_hide_cursors(self):
        #can probably simplify this logic, but it works
        set_state = tk.DISABLED
        if self.cursor_var.get():
            set_state = tk.NORMAL
        for row in Series_Control_Row.control_rows.values():
            row.radio_btn.configure(state = set_state)
        if set_state == tk.DISABLED:
            for cursor in SnaptoCursor.cursors.values():
                cursor.hide()
        else:
            for cursor in SnaptoCursor.cursors.values():
                cursor.show()
    def show_or_hide_all(self):
        for row in Series_Control_Row.control_rows.values():
            if row.checkvar.get() != self.checkvar2.get():
                row.checkbox.invoke()

class Edit_Series_Window(tk.Toplevel):
    """Edit Series Window is accessed via the '...' button in the series list.
    This window provides extra options for altering series data and display.
    Only one window may be open at any given time.
    Currently only scaling data is allowed from this window.
    """
    no_instance = True
    def __init__(self, master, series=None):
        Edit_Series_Window.no_instance = False
        tk.Toplevel.__init__(self, master)
        self.series = series
        self.scale = tk.DoubleVar()
        self.offset = tk.DoubleVar()
        self.scale.set(1)
        self.offset.set(0)
        self.title('Edit Series')
        self.lab_rescale = ttk.Label(master=self, text='Y Scale')
        self.protocol('WM_DELETE_WINDOW', self._quit)
        if self.series is not None:
            self.update_btn = ttk.Button(self,
                                        text = 'Rescale and Offset',
                                        command = self.update)
            self.adjustment_entry = ttk.Entry(self, textvariable=self.scale)
            self.lab_rescale.pack(fill=tk.BOTH, expand=1)
            self.adjustment_entry.pack(fill=tk.BOTH, expand=1)
            self.lab_offset = ttk.Label(master=self, text='Y offset')
            self.offset_entry = ttk.Entry(self, textvariable=self.offset)
            self.lab_offset.pack(fill=tk.BOTH, expand=1)
            self.offset_entry.pack(fill=tk.BOTH, expand=1)
            self.update_btn.pack(fill=tk.BOTH, expand=1)
            self.bind('<Return>', self.update)
        else:
            self.update_btn = ttk.Button(self,
                                        text = 'Rescale All Series',
                                        command = self.rescale_all_series)
            self.adjustment_entry = ttk.Entry(self, textvariable=self.scale)
            self.lab_rescale.pack(fill=tk.BOTH, expand=1)
            self.adjustment_entry.pack(fill=tk.BOTH, expand=1)
            self.update_btn.pack(fill=tk.BOTH, expand=1)
            self.adjustment_entry.bind('<Return>', self.rescale_all_series)
        self.adjustment_entry.focus()
        self.adjustment_entry.selection_range(0, tk.END)
    def _quit(self):
        Edit_Series_Window.no_instance = True
        self.destroy()
    def update(self, event=None):
        self.rescale_series()
        self.offset_series_y()
        #OH GOD NO WHY AM I DOING THIS. FIX IT FIX IT FIX IT FIX IT
        self.master.master.master.adjust_subplots()
        self._quit()
    def offset_series_y(self, event=None):
        offset = self.offset.get()
        self.series.offset_series_y(offset)
    def rescale_series(self, event=None):
        # Currently only scales the data. To update graphs, add or remove a graph.
        scale = self.scale.get()
        self.series.rescale_series(scale)
    def rescale_all_series(self, event=None):
        scale = self.scale.get()
        for series in Series.obj_list.values():
            series.rescale_series(scale)
        self.master.adjust_subplots()
        self._quit()

class Series_Control_Row(GUI):
    """ Control Row Class for series data.
    One of these will exist for every data series.
    There are options to select a cursor, remove/hide/show the graph.
    Extra options are allowed through use of the '...' button.
    """
    control_rows = {}
    def __init__(self, master, series):
        tk.Frame.__init__(self, master)
        self.configure(bd=1)
        self.var = tk.StringVar()
        self.var.set("1")
        self.checkvar = tk.BooleanVar()
        self.checkvar.set(1)
        self.series = series
        # self.label = series.label
        #fg=color option in tk items to change color
        self.radio_btn = ttk.Radiobutton(self,
                                    variable=self.master.master.radio_var,
                                    value=self.series.label,
                                    command=self.select_cursor)
        self.checkbox = ttk.Checkbutton(self,
                                    # width = 25,
                                    variable = self.checkvar,
                                    # text = self.series.label,
                                    command = self.show_or_hide_line)
        self.series_label = ttk.Label(self,
                                    width = 40,
                                    text = self.series.label)
        self.edit_button = ttk.Button(self,
                                    text="...",
                                    width = 3,
                                    command = self.open_edit_window)
        self.close_button = ttk.Button(self,
                                    text = "X",
                                    width = 3,
                                    command = self.remove_series)
        self.radio_btn.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.checkbox.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.series_label.grid(row=0, column=2, sticky=tk.N+tk.S)
        # self.edit_button.grid(row=0, column=3, padx = 1, sticky=tk.N+tk.S)
        # self.close_button.grid(row=0, column=4, padx = 100, sticky=tk.N+tk.S)
        self.edit_button.grid(row=0, column=3, padx = 4, sticky=tk.N+tk.S)
        self.close_button.grid(row=0, column=4, padx = 15, sticky=tk.N+tk.S)
        self.grid(sticky=tk.W+tk.E)
        # self.pack()
        Series_Control_Row.control_rows[self.series.label] = self
    def open_edit_window(self):
        if Edit_Series_Window.no_instance:
            Edit_Series_Window(self, self.series)
    # def get_scatter(self, ax):
    #     scatter = [scatter for scatter in ax.collections if scatter.get_label()==self.series.label][0]
    #     return scatter
    # def get_line(self, ax):
    #     line = [line for line in ax.lines if line.get_label()==self.series.label][0]
    #     return line
    def show_or_hide_cursor(self):
        todo()
    def show_or_hide_line(self):
        for artist in self.series.artists:
            artist.set_visible(self.checkvar.get())
        # for ax in self.master.master.fig.axes:
        #     self.get_line(ax).set_visible(self.checkvar.get())
        self.series.show = self.checkvar.get()
        self.master.master.legend = plt.legend()
        self.master.master.canvas.show()
    #FIXME Calling self.master.master... is probably a really dumb way to reach root window
    def remove_series(self):
        # for ax in self.master.master.fig.axes:
        #     if self.series.plot_type == 'scatter':
        #         ax.collections.remove(self.get_scatter(ax))
        #     else:
        #         ax.lines.remove(self.get_line(ax))
        for artist in self.series.artists:
            artist.remove()
        del Series.obj_list[self.series.label]
        del Series_Control_Row.control_rows[self.series.label]
        if self.master.master.radio_var.get() == self.series.label:
            for cursor in SnaptoCursor.cursors.values():
                cursor.update_series()
        del self.series
        self.master.master.legend = plt.legend()
        self.master.master.canvas.show()
        self.destroy()
    def select_cursor(self):
        for cursor in SnaptoCursor.cursors.values():
            cursor.update_series(self.series)
        # self.master.master.cursor[0].update_series(self.series)

#Series object stores information about the series to be graphed
class Series:
    """Main data variable for series data.
    """
    obj_list = {}
    largest = {}
    def __init__(self, x, y, path_to_csv, label=None):
        self.show = True
        self.x_title = []
        self.y_title = []
        self.x = x
        self.y = y
        self.plot_type = 'line'
        self.artists = []
        self.csv_path = path_to_csv
        self.remove_title_rows()
        self.x = [float(x) for x in self.x]
        self.y = [float(y) for y in self.y]
        self.x_range = [min(self.x), max(self.x)]
        self.y_range = [min(self.y), max(self.y)]
        self.y_max = max(self.y)
        self.peak_index = self.y.index(self.y_max)
        self.label = label
        if self.label is None:
            self.label = os.path.split(self.csv_path)[1].lower()[:-4]
        if self.y_title:
            ind = self.label.rfind(' - Series ')
            if ind:
                self.label = self.label[:ind]
            self.label = self.label + " - " + self.y_title[0]
        self.label = self.label.title()
        if self.label in Series.obj_list.keys():
            print('TODO: Add copy numbering')
            self.label = self.label + ' (1)'
        Series.obj_list[self.label] = self
    def is_number(self, s):
        # checks for invalid numerical data.
        try:
            float(s)
            return True
        except ValueError:
            return False
    def remove_title_rows(self):
        if not self.is_number(self.x[0]):
            self.x_title.append(self.x[0])
            self.y_title.append(self.y[0])
            " ".join(self.x_title)
            " ".join(self.y_title)
            self.x = self.x[1:]
            self.y = self.y[1:]
            self.remove_title_rows()
    def __str__(self):
        return self.csv_path
    def get_attr(self):
        print(self.label, self.csv_path, self.show)
    def offset_series_y(self, offset):
        for i in range(len(self.y)):
            self.y[i] += offset
    def rescale_series(self, scale):
        # Currently only scales the data. To update graphs, add or remove a graph.
        for i in range(len(self.y)):
            self.y[i] = self.y[i] * scale

def todo():
    print('TODO')

#TODO: Put this in a class somewhere?
def check_path(csv_path):
    return os.path.isfile(csv_path) and csv_path.lower().endswith(".csv")

def main():
    root = tk.Tk()
    app = GUI(root)
    app.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
    return 0

if __name__ == '__main__':
    main()
