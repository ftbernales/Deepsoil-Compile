import pandas as pd
import random

# Some sample data to plot.
cat_1 = ['y1', 'y2', 'y3', 'y4']
index_1 = range(0, 21, 1)
multi_iter1 = {}
for cat in cat_1:
    multi_iter1[cat] = [random.randint(10, 100) for x in index_1]

df = pd.DataFrame(multi_iter1, index=index_1)

excel_file = 'chart_legend.xlsx'
sheet_name = 'Sheet1'

writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
df.to_excel(writer, sheet_name=sheet_name)

workbook = writer.book
worksheet = writer.sheets[sheet_name]

chart = workbook.add_chart({'type': 'line'})

for i in range(len(cat_1)):
    col = i + 1
    chart.add_series({
        'name':       ['Sheet1', 0, col],
        'categories': ['Sheet1', 1, 0, 21, 0],
        'values':     ['Sheet1', 1, col, 21, col],
        'line': {
            'color':    '#D9D9D9',
            'width':    0.25,
        }
    })

chart.set_legend({'position': 'none'})

# Configure the chart axes.
chart.set_x_axis({'name': 'Index'})
chart.set_y_axis({'name': 'Value', 'major_gridlines': {'visible': False}})

# Insert the chart into the worksheet.
worksheet.insert_chart('G2', chart)

# Close the Pandas Excel writer and output the Excel file.
writer.save()