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
from tkinter import messagebox

#Series object stores information about the series to be graphed
class Series:
    obj_list = {}
    fig = plt.figure()
    def __init__(self, path_to_csv):
        self.show = True
        self.x = []
        self.y = []
        self.csv_path = path_to_csv
        self.label = os.path.split(self.csv_path)[1].lower()[:-4]
        self.readin_csv()
        # self.remove_title_rows()
        Series.obj_list[self.label] = self
    def readin_csv(self):
        with open(self.csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.x.append(row[0])
                self.y.append(row[1])
    def remove_title_rows(self):
        print("TODO: REMOVE TITLE ROWS")
        # make some code to remove title rows
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
    # def generate_fig():
    def update_fig(self):
        print('updating fig')
        for series in Series.obj_list.values():
            p1.plot(series.x, series.y, label=series.label)
    def plot_series(self):
        p1 = Series.fig.add_subplot(111)
        # p1 = fig.add_subplot(211)
        # p2 = fig.add_subplot(223)
        # p3 = fig.add_subplot(224)
        for series in Series.obj_list.values():
            p1.plot(series.x, series.y, label=series.label)
            # p2.plot(Series.obj_list[series].x, Series.obj_list[series].y, label=Series.obj_list[series].label)
            # p3.plot(Series.obj_list[series].x, Series.obj_list[series].y, label=Series.obj_list[series].label)
        #adjust settings
        p1.set_xlabel('Frequency (kHz)')
        p1.set_ylabel('Amplitude (V)')
        p1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
        p1.set_xlim(0, 1)
        plt.legend()
        return fig

#checks if csv file exists in specified path
def check_path(csv_path):
    return os.path.isfile(csv_path) and csv_path.lower().endswith(".csv")

def export_csv():
    fname = tk.filedialog.asksaveasfilename(filetypes=(("csv", "*.csv"),
        ("All files", "*.*") ))
    if fname:
        write_csv(fname)

#TODO: Needs a lot of work
def plot_graphs():
    fig = plt.figure()
    p1 = fig.add_subplot(111)
    # p1 = fig.add_subplot(211)
    # p2 = fig.add_subplot(223)
    # p3 = fig.add_subplot(224)
    for series in Series.obj_list.values():
        p1.plot(series.x, series.y, label=series.label)
        # p2.plot(Series.obj_list[series].x, Series.obj_list[series].y, label=Series.obj_list[series].label)
        # p3.plot(Series.obj_list[series].x, Series.obj_list[series].y, label=Series.obj_list[series].label)
    #adjust settings
    print(p1.lines)
    p1.set_xlabel('Frequency (kHz)')
    p1.set_ylabel('Amplitude (V)')
    p1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
    p1.set_xlim(0, 1)
    plt.legend()
    return fig

#TODO: Needs a lot of work
def write_csv(of):
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

def load_file():
    fname = tk.filedialog.askopenfilename(filetypes=(("Csv files", "*.csv"),
        ("All files", "*.*")))
    if fname:
        try:
            Series(fname)
        except:                     # <- naked except is a bad idea
            tk.messagebox.showerror("Open Source File", "Failed to read file\n'%s'" % fname)
        return

def main():
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
    root.title("CSV Grapher")

    #plot that ish
    fig = plot_graphs()

    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def _quit():
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    export_button = ttk.Button(master=root, text='Export CSV', command=export_csv)
    export_button.pack()

    quit_button = ttk.Button(master=root, text='Quit', command=_quit)
    quit_button.pack()

    open_button = ttk.Button(master=root, text="Add file...", command=load_file)
    open_button.pack()

    tk.mainloop()
    # If you put root.destroy() here, it will cause an error if
    # the window is closed with the window manager.

    return 0

if __name__ == '__main__':
    main()
