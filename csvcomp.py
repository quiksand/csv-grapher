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

class GUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title("CSV Grapher")
        master.protocol('WM_DELETE_WINDOW', self._quit)
        self.no_of_subplots = 1
        self.subplot_layouts = [[111],[211,212],[211,223,224],[221,222,223,224]]
        #export button
        self.export_button = ttk.Button(self,
                                    text='Export CSV',
                                    command=self.export_csv)
        self.export_button.pack()
        #quit button
        self.quit_button = ttk.Button(self,
                                    text='Quit',
                                    command=self._quit)
        self.quit_button.pack()
        self.open_button = ttk.Button(self,
                                    text="Add file...",
                                    command=self.load_file)
        self.open_button.pack()
        #close button
        close_button = ttk.Button(self,
                                    text="Remove file...",
                                    command=self.remove_series)
        close_button.pack()
        #button to add a subplot to figure
        add_plot_button = ttk.Button(self,
                                    text="Add plot",
                                    command=self.add_a_subplot)
        add_plot_button.pack()
        #button to remove a subplot from figure
        remove_plot_button = ttk.Button(self,
                                    text="Remove Plot",
                                    command=self.remove_a_subplot)
        remove_plot_button.pack()


        self.fig = plt.figure()
        # self.p1 = self.fig.add_subplot(111)
        # self.p1.set_xlabel('Frequency (kHz)')
        # self.p1.set_ylabel('Amplitude (V)')
        # self.p1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
        # self.p1.set_xlim(0, 1)
        # for series in Series.obj_list.values():
        #     if series.show:
        #         self.p1.plot(series.x, series.y, label=series.label)
        # self.leg = plt.legend()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.adjust_subplots()

    def set_axes(self):
        self.fig = plt.figure()
        self.p1 = self.fig.add_subplot(111)
        self.p1.set_xlabel('Frequency (kHz)')
        self.p1.set_ylabel('Amplitude (V)')
        self.p1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
        self.p1.set_xlim(0, 1)
    def plot_series(self, series):
        for ax in self.fig.axes:
            if series.show:
                ax.plot(series.x, series.y, label=series.label)
                self.legend = plt.legend()
        self.canvas.show()
    def plot_multiple_series(self):
        for series in Series.obj_list.values():
            self.plot_series(series)
    def adjust_subplots(self):
        self.fig.clear()
        self.subplots = [None]*self.no_of_subplots
        for i, j in enumerate(self.subplot_layouts[self.no_of_subplots-1]):
            self.subplots[i] = self.fig.add_subplot(j)
        self.plot_multiple_series()
        self.canvas.show()
        # self.canvas.draw()
    def add_a_subplot(self):
        if self.no_of_subplots < 4:
            self.no_of_subplots += 1
        self.adjust_subplots()
    def remove_a_subplot(self):
        if self.no_of_subplots > 1:
            self.no_of_subplots -= 1
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
    #TODO: Change behavior so graphs are selectable
    #TODO: Change so graphs don't update with Series.obj_list after they have been "deleted"
    def remove_series(self):
        for ax in self.fig.axes:
            ax.lines[0].remove()
        self.canvas.show()
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


#Series object stores information about the series to be graphed
class Series:
    obj_list = {}
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
