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

def plot_graphs(graphs):
    # set up figure
    fig = plt.figure(figsize=(9,5))
    p1 = fig.add_subplot(211)
    p2 = fig.add_subplot(223)
    p3 = fig.add_subplot(224)

    for graph in graphs:
        p1.plot(graphs[graph][0],graphs[graph][1], label=graph)
        p2.plot(graphs[graph][0],graphs[graph][1], label=graph)
        p3.plot(graphs[graph][0],graphs[graph][1], label=graph)

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
    plt.show()

def main():
    #argument parsing
    parser = argparse.ArgumentParser(description="Plots one or more .csv files")
    parser.add_argument('-f', dest='f', required = False,
        help="Specify path to a csv file to graph")
    parser.add_argument('-d', dest='dir', default='./', required = False,
        help="Specify a directory of csv files to graph")
    args = parser.parse_args()

    #graphs dict holds all graphs to be plotted
    graphs = {}

    #procedure if file is specified
    if args.f:
        #check existence and format of file to be opened
        if not (os.path.isfile(args.f) and args.f.lower().endswith(".csv")):
            print("Error: File path does not exist or is not correct format")
            return 1
        #open file and save to graphs dict
        x_temp = []
        y_temp = []
        with open(args.f, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                x_temp.append(row[0])
                y_temp.append(row[1])
        graphs[args.f[:-4]] = [x_temp, y_temp]

    #procedure if directory is given or file not specified
    else:
        #open files in directory and save to graphs dict if correct format
        for f in os.listdir(args.dir):
            x_temp = []
            y_temp = []
            graph_path = os.path.join(args.dir, f)
            if os.path.isfile(graph_path) and f.lower().endswith(".csv"):
                with open(graph_path, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        x_temp.append(row[0])
                        y_temp.append(row[1])
                graphs[f.lower()[:-4]] = [x_temp, y_temp, graph_path]

    plot_graphs(graphs)

    # app = Application(fig)
    # app.master.title('Sample application')
    # app.mainloop()

    #it's over... go home.
    print("Terminating script")

if __name__ == '__main__':
    main()
