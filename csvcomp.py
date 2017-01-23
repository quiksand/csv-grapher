import csv
import sys
import argparse
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import tkinter as tk
from tkinter import ttk

# class Application(tk.Frame):
#     def __init__(self, figure, master=None):
#         tk.Frame.__init__(self, master)
#         self.grid()
#         self.createWidgets()
#         print('jere 1')
#
#         canvas = FigureCanvasTkAgg(figure, self)
#         print(figure)
#         print(canvas)
#         canvas.show()
#         print('here3')
#         canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
#         print('here4')
#         toolbar = NavigationToolbar2TkAgg(canvas, self)
#         toolbar.update()
#         canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#
#
#     def createWidgets(self):
#         self.quitButton = ttk.Button(self, text='Quit', command=self.quit)
#         self.quitButton.grid()

#graphs dict holds all graphs to be plotted
graphs = {}

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

def check_path(graph_path):
    return os.path.isfile(graph_path) and graph_path.lower().endswith(".csv")

def create_graph(graph_path):
    x_temp = []
    y_temp = []
    with open(graph_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            x_temp.append(row[0])
            y_temp.append(row[1])
    graph_name = os.path.split(graph_path)[1].lower()[:-4]
    graphs[graph_name] = [x_temp, y_temp, graph_path]

def plot_graphs():
    # set up figure
    fig = plt.figure(figsize=(9,5))
    p1 = fig.add_subplot(211)
    p2 = fig.add_subplot(223)
    p3 = fig.add_subplot(224)

    for series in graphs:
        # print(graphs[series].get_attr())
        p1.plot(graphs[series].x,graphs[series].y, label=graphs[series].label)
        p2.plot(graphs[series].x,graphs[series].y, label=graphs[series].label)
        p3.plot(graphs[series].x,graphs[series].y, label=graphs[series].label)

    #adjust settings
    p1.set_xlabel('Frequency (kHz)')
    p1.set_ylabel('Amplitude (V)')
    p1.set_xlim(0, 1)
    p1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
    p2.set_xlabel('Frequency (kHz)')
    p2.set_ylabel('Amplitude (V)')
    p2.set_xlim(2, 9)
    p2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
    p3.set_xlabel('Frequency (kHz)')
    p3.set_ylabel('Amplitude (V)')
    p3.set_xlim(40, 48)
    p3.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
    # p3.autoscale_view()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.show()
    return fig

def main():
    #argument parsing
    parser = argparse.ArgumentParser(description="Plots one or more .csv files")
    parser.add_argument('-f', dest='f', required = False,
        help="Specify path to a csv file to graph")
    parser.add_argument('-d', dest='dir', default='./', required = False,
        help="Specify a directory of csv files to graph")
    args = parser.parse_args()

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

    fig = plot_graphs()
    plt.show()

    # app = Application(fig)
    # app.master.title('Sample application')
    # app.mainloop()

    #it's over... go home.
    print("Terminating script")

if __name__ == '__main__':
    main()
