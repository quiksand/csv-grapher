import csv
import argparse
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

#TODO Rearrange widgets to make more sense in layout
class GUI(tk.Frame):
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
            # Series(csv_path)
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
        self.xlabel = ['Frequency (kHz)']*4
        self.ylabel = ['Amplitude (V)']*4
        self.testvar=tk.DoubleVar()
        self.radio_var = tk.StringVar()

        self.plot_controls_frame = tk.Frame(self)
        self.graph_frame = tk.Frame(self)
        self.toolbar_frame = tk.Frame(self)
        self.legend_list_frame = tk.Frame(self)
        self.export_button_frame = tk.Frame(self)

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
        self.test_button = ttk.Button(self.export_button_frame,
                                    text='Test Button',
                                    command=self.todo3)
        self.test_button_2 = ttk.Button(self.export_button_frame,
                                    text='Test Button 2',
                                    command=self.todo3)
        # self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        # self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=5, rowspan=5)

        # self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.Y, expand=0)
        # self.canvas._tkcanvas.grid(row=3, column=0, columnspan=5)

        self.adjust_subplots()
        self.add_all_list_items()

        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        self.open_button.grid(row=5, column=5)
        self.export_csv_button.pack()
        self.export_excel_button.pack()
        self.test_button.pack()
        self.test_button_2.pack()
        self.graph_frame.grid(row=0, column=0, columnspan=5, rowspan=5)
        self.legend_list_frame.grid(row=0, column=5)
        self.export_button_frame.grid(row=6, column=5)
        self.plot_controls_frame.grid(row=5, column=0, columnspan=5)
        self.add_plot_button.grid(row=6, column=2)
        self.remove_plot_button.grid(row=6, column=3)
        self.toolbar_frame.grid(row=7, column=0, columnspan=5, sticky=tk.W)

    def todo2(self, val):
        print(val)
    def todo3(self):
        Series.obj_list['delete'].x.pop()
        for series in Series.obj_list.values():
            print('\n')
            print(series.label)
            print(len(series.x), len(series.y))
            print('\n')
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
    def plot_series(self, series):
        series.axes_index = []
        for ax in self.fig.axes:
            ax.plot(series.x, series.y, label=series.label)
            series.axes_index.append(len(ax.lines))
            self.legend = plt.legend()
        self.canvas.show()
    def plot_multiple_series(self):
        for series in Series.obj_list.values():
            self.plot_series(series)
    def insert_plot_control(self, index):
        Plot_Control_Row(self.plot_controls_frame, index)
    def adjust_subplots(self):
        self.fig.clear()
        for i, j in enumerate(self.subplot_layouts[self.no_of_subplots-1]):
            if i not in Plot_Control_Row.plot_control_rows.keys():
                self.insert_plot_control(i)
            self.subplots[i] = self.fig.add_subplot(j)
            self.subplots[i].set_xlabel(self.xlabel[i])
            self.subplots[i].set_ylabel(self.ylabel[i])
        # self.rescale_axes()
        self.plot_multiple_series()
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
            self.no_of_subplots -= 1
        self.adjust_subplots()
    def _quit(self):
        self.master.quit()
        self.master.destroy()
    def export_excel(self):
        todo()
    def export_csv(self):
        #TODO: Simplify, possibly remove extra call to write_csv
        #TODO: Grey out button if no plots are in Series.obj_list
        fname = tk.filedialog.asksaveasfilename(filetypes=(("csv", "*.csv"),
            ("All files", "*.*") ))
        if fname:
            self.write_csv(fname)
    def write_csv(self, of):
        #TODO: Simplify. In future, add Excel functionality?
        labels = ['Frequency (kHz)']
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
    #TODO: Make this logic better -
    def load_file(self):
        fname = tk.filedialog.askopenfilename(filetypes=(("Csv files", "*.csv"),
            ("All files", "*.*")))
        if fname:
            # self.open_button.pack_forget()
            new_series = self.read_in_csv(fname)
            for series in new_series:
                self.plot_series(series)
                self.add_list_item(series)
            # self.open_button.pack()
    def add_list_item(self, series):
        Series_Control_Row(self.legend_list_frame, series)
    def add_all_list_items(self):
        for series in Series.obj_list.values():
            self.add_list_item(series)
    #TODO: Change behavior so graphs are selectable
    #TODO: Change so graphs don't update with Series.obj_list after they have been "deleted"

class Plot_Control_Row(GUI):
    plot_control_rows = {}
    def __init__(self, master, subplot_index):
        tk.Frame.__init__(self, master)
        self.subplot_index = subplot_index
        self.label = 'Plot {}'.format(self.subplot_index+1)
        self.x_lower_bound = tk.DoubleVar()
        # self.x_lower_bound = tk.StringVar()
        self.x_lower_bound.set(0)
        self.x_upper_bound = tk.DoubleVar()
        self.x_upper_bound.set(40)
        self.xbar = tk.DoubleVar()
        # self.xbar = tk.StringVar()
        # self.xbar.set(40.0)
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
                                    var = self.ybar,
                                    command = self.todo2)
        self.y_scale_box_upper = ttk.Entry(self,
                                    width = 5,
                                    textvariable = self.y_upper_bound)
        # Resize Button
        self.resize_button = ttk.Button(self,
                                    text = 'Rescale',
                                    command = self.update_x_bounds)

        # Packing
        self.plot_label.pack(side = tk.LEFT)
        self.x_scale_label.pack(side = tk.LEFT)
        self.x_scale_label.pack(side = tk.LEFT)
        self.x_scale_box_lower.pack(side = tk.LEFT)
        self.x_scale_box_lower.pack(side = tk.LEFT)
        self.x_scale_slider.pack(side = tk.LEFT)
        self.x_scale_box_upper.pack(side = tk.LEFT)
        self.x_scale_box_upper.pack(side = tk.LEFT)
        self.y_scale_label.pack(side = tk.LEFT)
        self.y_scale_box_lower.pack(side = tk.LEFT)
        self.y_scale_slider.pack(side = tk.LEFT)
        self.y_scale_box_upper.pack(side = tk.LEFT)
        self.resize_button.pack(side = tk.LEFT)
        self.pack()

        Plot_Control_Row.plot_control_rows[self.subplot_index]= self

    def todo2(self, val):
        print(val)
    #TODO: Put some validation code in for the boxes
    #TODO: Add in Y functionality
    #TODO: Rethink the way the slider scales
    def rescale_axes(self, a, b):
        self.master.master.subplots[self.subplot_index].set_xlim(a, b)
        self.master.master.canvas.show()
    def update_x_bounds(self):
        self.rescale_axes(self.x_lower_bound.get(), self.x_upper_bound.get())
        # self.xbar.set(1)
    def update_y_bounds(self):
        self.rescale_axes(self.y_lower_bound.get(), self.y_upper_bound.get())
        # self.ybar.set(1)
    def x_slider_moved(self, val):
        a = self.x_lower_bound.get()
        b = self.x_upper_bound.get()
        x = self.xbar.get()
        b = a+x*(b-a)
        self.rescale_axes(a, b)

class Series_Control_Row(GUI):
    control_rows = {}
    def __init__(self, master, series):
        tk.Frame.__init__(self, master)
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
        self.radio_btn.grid(row=0, column=0)
        self.checkbox = ttk.Checkbutton(self,
                                    width=25,
                                    variable=self.checkvar,
                                    text=self.series.label,
                                    command=self.show_or_hide_line)
        self.checkbox.grid(row=0, column=1)
        self.edit_button = ttk.Button(self,
                                    text="...",
                                    width=1,
                                    command=todo)
        self.edit_button.grid(row=0, column=2)
        self.close_button = ttk.Button(self,
                                    text="X",
                                    width=1,
                                    command=self.remove_series)
        self.close_button.grid(row=0, column=3)
        self.pack()
        Series_Control_Row.control_rows[self.series.label] = self
    def get_line(self, ax):
        line = [line for line in ax.lines if line.get_label()==self.series.label][0]
        return line
    def show_or_hide_line(self):
        for ax in self.master.master.fig.axes:
            self.get_line(ax).set_visible(self.checkvar.get())
        self.series.show = self.checkvar.get()
        self.master.master.canvas.show()

    #TODO Calling self.master.master... is probably a really dumb way to reach root window
    def remove_series(self):
        for ax in self.master.master.fig.axes:
            ax.lines.remove(self.get_line(ax))
        del Series.obj_list[self.series.label]
        del Series_Control_Row.control_rows[self.series.label]
        self.master.master.canvas.show()
        self.destroy()
        # print(Series_Control_Row.control_rows.keys())
        # print(Series.obj_list.keys())
    def select_cursor(self):
        print(self.master.master.radio_var.get())
        todo()

#Series object stores information about the series to be graphed
class Series:
    obj_list = {}
    def __init__(self, x, y, path_to_csv, label=None):
        print('TODO: Add copy numbering')
        print('TODO: clean up labeling')
        self.show = True
        self.x_title = []
        self.y_title = []
        self.x = x
        self.y = y
        self.axes_index = [None]*4
        self.csv_path = path_to_csv
        self.remove_title_rows()
        self.x_range = [min(self.x), max(self.x)]
        self.y_range = [min(self.y), max(self.y)]
        self.peak_index = self.x.index(max(self.x))
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
            self.label = self.label + ' (1)'
        Series.obj_list[self.label] = self
    def is_number(self, s):
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
