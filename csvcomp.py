import csv
# import sys
import argparse
import os
import matplotlib
matplotlib.use('TkAgg')
# from matplotlib.widgets import MultiCursor
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
# from tkinter.filedialog import askopenfilename
# from tkinter.messagebox import showerror

#graphs dict holds all series to be plotted - Move inside Series class
graphs = {}

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

def export_csv():
    print('TODO: Export CSV')
    write_csv('../CombinedCSV.csv')


#TODO: Needs a lot of work
def plot_graphs():
    # set up figure
    fig = plt.figure()#figsize=(9,5))
    p1 = fig.add_subplot(111)
    # p1 = fig.add_subplot(211)
    # p2 = fig.add_subplot(223)
    # p3 = fig.add_subplot(224)

    for series in graphs:
        # print(graphs[series].get_attr())
        p1.plot(graphs[series].x, graphs[series].y, label=graphs[series].label)
        # p2.plot(graphs[series].x, graphs[series].y, label=graphs[series].label)
        # p3.plot(graphs[series].x, graphs[series].y, label=graphs[series].label)

    #adjust settings
    # multi = MultiCursor(fig.canvas, (p1, p2), color='r', lw=1,
                    # horizOn=False, vertOn=True)
    p1.set_xlabel('Frequency (kHz)')
    p1.set_ylabel('Amplitude (V)')
    p1.set_xlim(0, 1)
    p1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
    # p2.set_xlabel('Frequency (kHz)')
    # p2.set_ylabel('Amplitude (V)')
    # p2.set_ylim(0, 0.00015)
    # p2.set_xlim(2, 12)
    # p2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.00e'))
    # p3.set_xlabel('Frequency (kHz)')
    # p3.set_ylabel('Amplitude (V)')
    # p3.set_ylim(0, 0.0001)
    # p3.set_xlim(36, 40)
    # p3.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
    # p3.autoscale_view()
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend()
    # plt.show()
    # fig.tight_layout()
    # plt.subplots_adjust(right=0.8)
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

def load_file():
    fname = tk.filedialog.askopenfilename(filetypes=(("Template files", "*.tplate"),
                                       ("HTML files", "*.html;*.htm"),
                                       ("All files", "*.*") ))
    if fname:
        try:
            print("""here it comes: self.settings["template"].set(fname)""")
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


    root = tk.Tk()
    root.title("CSV Grapher")
    # content = ttk.Frame(root)
    # content.grid()
    # frame = ttk.Frame(content, borderwidth=5, relief="sunken", width=200, height=100)
    # frame.grid()
    # namelbl = ttk.Label(content, text="Name")
    # name = ttk.Entry(content)


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
    # canvas.get_tk_widget().grid()
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    # canvas._tkcanvas.pack()
    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def _quit():
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    # newframe = tk.Frame(master=root)
    # newframe.grid(column=10, row=10)
    export_button = ttk.Button(master=root, text='Export CSV', command=export_csv)
    export_button.pack()

    quit_button = ttk.Button(master=root, text='Quit', command=_quit)
    quit_button.pack()

    open_button = ttk.Button(master=root, text="Add file...", command=load_file)
    open_button.pack()

    tk.mainloop()
    # If you put root.destroy() here, it will cause an error if
    # the window is closed with the window manager.







    # plt.show()

    #remove when feature is better developed
    #for now, combine everything in graphs into one csv and print it
    # write_csv(args.of)

    #it's over... go home.
    print("Terminating script")


    # app.mainloop()

    return 0

if __name__ == '__main__':
    main()
#
#
# from tkinter import *
# from tkinter import ttk
#
# root = Tk()
#
# content = ttk.Frame(root)
# frame = ttk.Frame(content, borderwidth=5, relief="sunken", width=200, height=100)
# namelbl = ttk.Label(content, text="Name")
# name = ttk.Entry(content)
#
# onevar = BooleanVar()
# twovar = BooleanVar()
# threevar = BooleanVar()
# onevar.set(True)
# twovar.set(False)
# threevar.set(True)
#
# one = ttk.Checkbutton(content, text="One", variable=onevar, onvalue=True)
# two = ttk.Checkbutton(content, text="Two", variable=twovar, onvalue=True)
# three = ttk.Checkbutton(content, text="Three", variable=threevar, onvalue=True)
# ok = ttk.Button(content, text="Okay")
# cancel = ttk.Button(content, text="Cancel")
#
# content.grid(column=0, row=0)
# frame.grid(column=0, row=0, columnspan=3, rowspan=2)
# namelbl.grid(column=3, row=0, columnspan=2)
# name.grid(column=3, row=1, columnspan=2)
# one.grid(column=0, row=3)
# two.grid(column=1, row=3)
# three.grid(column=2, row=3)
# ok.grid(column=3, row=3)
# cancel.grid(column=4, row=3)
#
# root.mainloop()
