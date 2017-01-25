import csv
# import sys
import argparse
import os
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.widgets import MultiCursor
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import tkinter as tk
from tkinter import ttk

#graphs dict holds all series to be plotted
graphs = {}

#tk application
# class Application(tk.Frame):
#     def __init__(self, master=None):
#         tk.Frame.__init__(self, master)
#         self.grid()
#         self.createWidgets()
#
#     def createWidgets(self):
#         self.quitButton = ttk.Button(self, text='Quit', command=self.quit)
#         self.quitButton.grid()


#Series object stores information about the series to be graphed
class Series:
    def __init__(self, graph_path):
        self.show = True
        self.x = []
        self.y = []
        self.graph_path = graph_path
        self.label = os.path.split(graph_path)[1].lower()[:-4]
        with open(graph_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.x.append(row[0])
                self.y.append(row[1])
        graphs[self.label] = self
    def __del__(self):
        del graphs[self.label]
    def __str__(self):
        return self.graph_path
    def get_attr(self):
        print(self.label, self.graph_path, self.show)
    def show(self):
        self.show = True
    def hide(self):
        self.show = False

#checks if csv file exists in specified path
def check_path(graph_path):
    return os.path.isfile(graph_path) and graph_path.lower().endswith(".csv")

#TODO: Needs a lot of work
def plot_graphs():
    # set up figure
    fig = plt.figure()#figsize=(9,5))
    p1 = fig.add_subplot(211)
    p2 = fig.add_subplot(223)
    p3 = fig.add_subplot(224)

    for series in graphs:
        # print(graphs[series].get_attr())
        p1.plot(graphs[series].x, graphs[series].y, label=graphs[series].label)
        p2.plot(graphs[series].x, graphs[series].y, label=graphs[series].label)
        p3.plot(graphs[series].x, graphs[series].y, label=graphs[series].label)

    #adjust settings
    multi = MultiCursor(fig.canvas, (p1, p2), color='r', lw=1,
                    horizOn=False, vertOn=True)
    p1.set_xlabel('Frequency (kHz)')
    p1.set_ylabel('Amplitude (V)')
    p1.set_xlim(0, 1)
    p1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
    p2.set_xlabel('Frequency (kHz)')
    p2.set_ylabel('Amplitude (V)')
    p2.set_ylim(0, 0.00015)
    p2.set_xlim(2, 12)
    p2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.00e'))
    p3.set_xlabel('Frequency (kHz)')
    # p3.set_ylabel('Amplitude (V)')
    p3.set_ylim(0, 0.0001)
    p3.set_xlim(36, 40)
    p3.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
    # p3.autoscale_view()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.show()
    fig.tight_layout()
    plt.subplots_adjust(right=0.8)
    return fig

#TODO: Needs a lot of work
def write_csv(of):
    labels = ['Frequency (kHz)']
    xs = []
    ys = []
    rows = []
    for series in graphs:
        labels.append(graphs[series].label)
        xs.append(graphs[series].x)
        ys.append(graphs[series].y)
    rows.append(labels)
    for index, val in enumerate(xs[0], start = 0):
        # print(index, val)
        rows.append([])
        rows[index+1].append(xs[0][index])
        for y in ys:
            rows[index+1].append(y[index])
    with open(of, 'w', newline='') as newcsv:
        writer = csv.writer(newcsv)
        writer.writerows(rows)

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


    root = tk.Tk()
    root.title("CSV Grapher")
    # content = ttk.Frame(root)
    # root.geometry("800x600+10+10")
    # root.resizable(0, 0)
    # app = Application(master=root)


    #procedure if file is specified
    if args.f:
        #open file and save to graphs dict if correct format
        graph_path = os.path.abspath(args.f)
        if not check_path(graph_path):
            print("Error: File path does not exist or is not correct format")
            return 1
        # create_graph(graph_path)
        Series(graph_path)

    #procedure if directory is given or file not specified
    else:
        #open files in directory and save to graphs dict if correct format
        for f in os.listdir(args.dir):
            graph_path = os.path.abspath(os.path.join(args.dir, f))
            if check_path(graph_path):
                Series(graph_path)

    #plot that ish
    fig = plot_graphs()

    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(fig, master=root)
    # canvas.show()
    canvas.get_tk_widget().grid(column=0, row=0, rowspan=5, sticky="NW")
    # canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def _quit():
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    newframe = tk.Frame(master=root)
    newframe.grid(column=10, row=10)
    button = tk.Button(master=newframe, text='QuitFUCK!!!', command=_quit)
    button.pack(side=tk.LEFT)
    #
    # button = tk.Button(master=root, text='Quit', command=_quit)
    # button.pack()

    tk.mainloop()
    # If you put root.destroy() here, it will cause an error if
    # the window is closed with the window manager.







    # plt.show()

    #for now, combine everything in graphs into one csv and print it
    write_csv(args.of)

    #it's over... go home.
    print("Terminating script")


    # app.mainloop()

    return 0

if __name__ == '__main__':
    main()
