import xlsxwriter as xw

def testfunc(series_list):
    print('testfunc')
    write_series_to_excel(series_list)

class Excel_GUI(tk.Toplevel):
    no_instance = True
    def __init__(self, master, series):
        Edit_Series_Window.no_instance = False
        tk.Toplevel.__init__(self, master)
        self.series = series
        self.title('Edit Series')
        self.blah = ttk.Label(master=self, text='Put something Here!!')
        self.blah.pack(fill=tk.BOTH, expand=1)
    def __del__(self):
        Edit_Series_Window.no_instance = True

#main excel writing function
def write_series_to_excel(series_list, options={'graph':True}):
    '''Takes a list of series and writes them to excel workbook'''
    workbook = xw.Workbook('combined.xlsx')
    worksheet = workbook.add_worksheet()
    if options['graph']:
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
            add_series_to_chart(series, col, chart)
        col += 1
    if options['graph']:
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

def graph_excel(workbook, worksheet):
    chart = workbook.add_chart({'type': 'scatter', 'subtype':'straight'})
    # chart.add_series({
    #                     'name':       '=Sheet1!$B$1',
    #                     'categories': '=Sheet1!$A$2:$A$4096',
    #                     'values':     '=Sheet1!$B$2:$B$4096'
    #                     })
    chart.add_series({
                        'name': ['Sheet1', 0, 1, 0, 1],
                        'categories': ['Sheet1', 1, 0, 4096, 0],
                        'values': ['Sheet1', 1, 1, 4096, 1]
                        })
    worksheet.insert_chart('A7', chart)

def main():
    workbook = xw.Workbook('hello.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write('A1', 'Hello world')

    workbook.close()


if __name__ == '__main__':
    main()
