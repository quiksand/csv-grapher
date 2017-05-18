import xlsxwriter as xw
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csvcomp

def testfunc(series_list):
    print(series_list)
    write_series_to_excel(series_list)

class Excel_Series_Options_Row(tk.Frame):
    def __init__(self, master, row):
        self.series_label = ttk.Label(self,
                                    text= row.series.label)
        for i in range(self.master.no_of_subplots):
            print('hello')
        self.grid()

class Excel_Export_Window(tk.Toplevel):
    no_instance = True
    def __init__(self, master):
        Excel_Export_Window.no_instance = False
        tk.Toplevel.__init__(self, master)
        self.title('Export to Excel')
        self.blah = ttk.Label(master=self, text='Put something Here!!')
        self.blah.pack(fill=tk.BOTH, expand=1)
        self.series_options_frame = ttk.Frame(self)
        # self.plot_options_frame = tk.Frame(self, bg="black", bd=1)
        print(csvcomp.Series_Control_Row.control_rows.values())
        print(len(csvcomp.Series_Control_Row.control_rows))
        for row in csvcomp.Series_Control_Row.control_rows.keys():
            print('HERE')
            # Excel_Series_Options_Row(series_options_frame, row)
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
def write_series_to_excel(series_list, options={'graph':True}):
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
        worksheet.insert_chart('B7', chart, {'x_scale': 2.5, 'y_scale': 2})
        add_chart_props(chart)
    # graph_excel(workbook, worksheet)
    workbook.close()
    print('Created Excel workbook')

def add_series_to_chart(series, col, chart):
    chart.add_series({
                        'name': ['Sheet1', 0, col, 0, col],
                        'categories': ['Sheet1', 1, col-1, len(series.x), col-1],
                        'values': ['Sheet1', 1, col, len(series.x), col]
                        })

def add_chart_props(chart):
    chart.set_legend({
        'position': 'overlay_right',
        'font': {'size': 12}
        })
    chart.set_title({
        'name': 'CHANGEME',
        'name_font': {'bold': False, 'size': 14}
        })
    chart.set_y_axis({
        'name': 'RMS Amplitude (nm)',
        'major_gridlines': {'visible': True},
        'name_font': {'bold': False, 'size': 12}
        })
    chart.set_x_axis({
        'name': 'Frequency (kHz)',
        'major_gridlines': {'visible': True},
        'name_font': {'bold': False, 'size': 12},
        'max': 2.0
        })
# def graph_excel(workbook, worksheet):
#     chart = workbook.add_chart({'type': 'scatter', 'subtype':'straight'})
#     # chart.add_series({
#     #                     'name':       '=Sheet1!$B$1',
#     #                     'categories': '=Sheet1!$A$2:$A$4096',
#     #                     'values':     '=Sheet1!$B$2:$B$4096'
#     #                     })
#     chart.add_series({
#                         'name': ['Sheet1', 0, 1, 0, 1],
#                         'categories': ['Sheet1', 1, 0, 4096, 0],
#                         'values': ['Sheet1', 1, 1, 4096, 1]
#                         })
#     worksheet.insert_chart('A7', chart)




def main():
    workbook = xw.Workbook('hello.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write('A1', 'Hello world')

    workbook.close()


if __name__ == '__main__':
    main()
