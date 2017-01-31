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
        tk.Frame.__init__(self, master)
        master.title("CSV Grapher")
        master.protocol('WM_DELETE_WINDOW', self._quit)
        self.no_of_subplots = 1
        self.subplot_layouts = [[111],[211,212],[211,223,224],[221,222,223,224]]
        self.subplots = [None]*self.no_of_subplots
        self.xscale = tk.StringVar()
        self.yscale = tk.StringVar()
        self.xscale.set(0.8)
        self.yscale.set(0.005)
        #export button
        self.export_button = ttk.Button(self,
                                    text='Export CSV',
                                    command=self.export_csv)
        # self.export_button.pack(side=tk.LEFT)
        self.export_button.grid(row=6, column=0)
        #quit button
        # self.quit_button = ttk.Button(self,
        #                             text='Quit',
        #                             command=self._quit)
        # self.quit_button.pack()
        self.open_button = ttk.Button(self,
                                    text="Add file",
                                    command=self.load_file)
        # self.open_button.pack(side=tk.LEFT)
        self.open_button.grid(row=6, column=1)
        self.add_plot_button = ttk.Button(self,
                                    text="Add plot",
                                    command=self.add_a_subplot)
        # self.add_plot_button.pack(side=tk.LEFT)
        self.add_plot_button.grid(row=6, column=2)
        #button to remove a subplot from figure
        self.remove_plot_button = ttk.Button(self,
                                    text="Remove Plot",
                                    command=self.remove_a_subplot)
        # self.remove_plot_button.pack(side=tk.LEFT)
        self.remove_plot_button.grid(row=6, column=3)
        self.xscale_label = ttk.Label(self, text='X:', width=9, anchor=tk.E)
        self.xscale_label.grid(row=5, column=0)
        self.xscale_box = ttk.Entry(self,
                                    width=9,
                                    textvariable=self.xscale)
        # self.xscale_box.pack()
        self.xscale_box.grid(row=5, column=1)
        # self.xbtn = ttk.Button(self,
        #                             text="Rescale X",
        #                             command=self.rescale_axes)
        # self.xbtn.pack()
        self.yscale_label = ttk.Label(self, text='Y:', width=9, anchor=tk.E)
        self.yscale_label.grid(row=5, column=3)
        self.yscale_box = ttk.Entry(self,
                                    width=9,
                                    textvariable=self.yscale)
        # self.yscale_box.pack()
        self.yscale_box.grid(row=5, column=4)
        self.resize_button = ttk.Button(self,
                                    text="Rescale",
                                    command=self.rescale_axes)
        # self.resize_button.pack()
        self.resize_button.grid(row=5, column=2)

        self.fig = plt.figure()

        self.graph_frame = tk.Frame(self)
        self.graph_frame.grid(row=0, column=0, columnspan=5, rowspan=5)
        # self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        # self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=5, rowspan=5)

        self.toolbar_frame = tk.Frame(self)
        self.toolbar_frame.grid(row=7, column=0, columnspan=5, sticky=tk.W)
        # self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.Y, expand=0)
        # self.canvas._tkcanvas.grid(row=3, column=0, columnspan=5)

        self.adjust_subplots()
        #test list widget

        self.test = tk.Frame(self)
        self.add_all_list_items()
        # self.test.pack(side=tk.RIGHT)
        self.test.grid(row=0, column=5)

    def rescale_axes(self):
        self.xscale = self.xscale_box.get()
        self.yscale = self.yscale_box.get()
        for i in range(self.no_of_subplots):
            self.subplots[i].set_xlim(0, float(self.xscale))
            self.subplots[i].set_ylim(0, float(self.yscale))
            self.canvas.show()
            # self.canvas.draw()
        self.xscale_box.delete(0, tk.END)
        self.yscale_box.delete(0, tk.END)
        self.xscale_box.insert(0, self.xscale)
        self.yscale_box.insert(0, self.yscale)
    def plot_series(self, series):
        for ax in self.fig.axes:
            if series.show:
                ax.plot(series.x, series.y, label=series.label)
                series.axes_index = len(ax.lines)
                self.legend = plt.legend()
        self.canvas.show()
    def plot_multiple_series(self):
        for series in Series.obj_list.values():
            self.plot_series(series)
    def adjust_subplots(self):
        self.fig.clear()
        for i, j in enumerate(self.subplot_layouts[self.no_of_subplots-1]):
            self.subplots[i] = self.fig.add_subplot(j)
            self.subplots[i].set_xlabel('Frequency (kHz)')
            self.subplots[i].set_ylabel('Amplitude (V)')
        self.rescale_axes()
        self.plot_multiple_series()
        self.fig.tight_layout()
        self.canvas.show()
        # self.canvas.draw()
    def add_a_subplot(self):
        if self.no_of_subplots < 4:
            self.no_of_subplots += 1
            self.subplots.append(None)
        self.adjust_subplots()
    def remove_a_subplot(self):
        if self.no_of_subplots > 1:
            self.no_of_subplots -= 1
            del self.subplots[-1]
        self.adjust_subplots()
    def _quit(self):
        self.master.quit()
        self.master.destroy()
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
    def load_file(self):
        fname = tk.filedialog.askopenfilename(filetypes=(("Csv files", "*.csv"),
            ("All files", "*.*")))
        if fname:
                new_series = Series(fname)
                self.plot_series(new_series)
                self.add_list_item(new_series)
    def add_list_item(self, series):
        Ctrl_Row(self.test, series)
    def add_all_list_items(self):
        for series in Series.obj_list.values():
            self.add_list_item(series)
    #TODO: Change behavior so graphs are selectable
    #TODO: Change so graphs don't update with Series.obj_list after they have been "deleted"
    def remove_list_item(self):
        # del Ctrl_Row.control_rows[]
        todo()

class Ctrl_Row(GUI):
    control_rows = {}
    def __init__(self, master, series):
        tk.Frame.__init__(self, master)
        self.var = tk.StringVar()
        self.checkvar = tk.BooleanVar()
        self.checkvar.set(1)
        self.series = series
        #fg=color option in tk items to change color
        self.radio_btn = ttk.Radiobutton(self,
                                    variable=self.var,
                                    value=self.series.label,
                                    command=self.select_cursor)
        self.radio_btn.grid(row=0, column=0)
        self.checkbox = ttk.Checkbutton(self,
                                    # onvalue=True,
                                    # offvalue=False,
                                    width=25,
                                    variable=self.checkvar,
                                    # variable=self.series.show,
                                    text=self.series.label,
                                    command=self.cb)
        self.checkbox.grid(row=0, column=1)
        self.close_button = ttk.Button(self,
                                    text="X",
                                    width=1,
                                    command=self.remove_series)
        self.close_button.grid(row=0, column=2)
        # self.pack()
        self.grid()
        self.label = series.label
        Ctrl_Row.control_rows[series.label] = self
    #TODO Check this and all __del__() methods to make sure they are doing anything
    # def __del__(self):
        # del Series.obj_list[self.label]
        # del Ctrl_Row.control_rows[self.label]
    #TODO Make this update faster (play with artists)
    def cb(self):
        self.series.show = self.checkvar.get()
        self.master.master.adjust_subplots()

    #TODO Calling self.master.master... is probably a really dumb way to reach root window
    def remove_series(self):
        for ax in self.master.master.fig.axes:
            line = [line for line in ax.lines if line.get_label()==self.label][0]
            ax.lines.remove(line)
        del Series.obj_list[self.label]
        del Ctrl_Row.control_rows[self.label]
            # ax.lines.remove(self.label)
        # self.master.master.fig.axes.lines.remove(self.label)
        # del self
        self.master.master.canvas.show()
        self.destroy()
    def select_cursor(self):
        todo()

#Series object stores information about the series to be graphed
class Series:
    obj_list = {}
    def __init__(self, path_to_csv):
        # self.show = True
        self.show = True
        self.x = []
        self.y = []
        self.axes_index = [None]*4
        self.csv_path = path_to_csv
        self.label = os.path.split(self.csv_path)[1].lower()[:-4]
        self.readin_csv()
        # self.btn_row = SeriesList(self)
        # self.remove_title_rows()
        Series.obj_list[self.label] = self
    def readin_csv(self):
        with open(self.csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.x.append(row[0])
                self.y.append(row[1])
    def remove_title_rows(self):
        print("TODO: Remove title rows from csvs that have them")
    def __del__(self):
        del Series.obj_list[self.label]
    def __str__(self):
        return self.csv_path
    def get_attr(self):
        print(self.label, self.csv_path, self.show)
    def show(self):
        self.show = True
    def hide(self):
        self.show = False

def todo():
    print('TODO')

#TODO: Put this in a class somewhere?
def check_path(csv_path):
    return os.path.isfile(csv_path) and csv_path.lower().endswith(".csv")

def main():
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
        # create_graph(csv_path)
        Series(csv_path)

    #procedure if directory is given or file not specified
    else:
        #open files in directory and save to graphs dict if correct format
        for f in os.listdir(args.dir):
            csv_path = os.path.abspath(os.path.join(args.dir, f))
            if check_path(csv_path):
                Series(csv_path)

    root = tk.Tk()
    app = GUI(root)
    app.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
    return 0

if __name__ == '__main__':
    main()
