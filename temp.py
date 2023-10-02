import PySimpleGUI as sg
import pandas as pd

# Function to guess the delimiter used in a CSV file
def guess_delimiter(file_path):
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()

    delimiters = [';', ',', ' ']
    for delimiter in delimiters:
        if delimiter in first_line:
            return delimiter
    return None

# File picker window
layout = [
    [sg.Text('Please select the file to open')],
    [sg.Input(), sg.FileBrowse(file_types=(("Excel Files", "*.xls;*.xlsx"), ("CSV Files", "*.csv")))],
    [sg.OK(), sg.Cancel()]
]

window = sg.Window('File Picker', layout)
event, values = window.read()
window.close()

# Check for cancel or window close
if event in [sg.WINDOW_CLOSED, 'Cancel']:
    exit()

file_path = values[0]
df = None

# Read the file using appropriate method
if file_path.endswith('.csv'):
    delimiter = guess_delimiter(file_path)
    df = pd.read_csv(file_path, delimiter=delimiter)
elif file_path.endswith(('.xls', '.xlsx')):
    df = pd.read_excel(file_path)

if df is None:
    sg.popup_error("Unsupported file type.")
    exit()

data_list = df.values.tolist()
headers = list(df.columns)

# Layout for the data display and interactive part
layout = [
    [sg.Table(values=data_list, headings=headers, auto_size_columns=True,
              num_rows=min(25, len(data_list)), display_row_numbers=True, key='-TABLE-')],
    [sg.Text('Function Column:'), sg.Combo(headers, key='-FUNC-', size=(15, 1)),
     sg.Text('Argument Column(s):'), sg.Listbox(values=headers, key='-ARGS-', size=(15, 5), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE),
     sg.Text('Assessment:'), sg.Combo(['Minimize', 'Maximize'], key='-ASSESS-', size=(10, 1))],
    [sg.Button("Apply"), sg.Button("Exit")],
    [sg.Table(values=[["" for _ in range(len(headers))]], headings=headers, auto_size_columns=True,
              num_rows=min(25, len(data_list)), display_row_numbers=True, key='-TABLE2-')]
]

window = sg.Window('Data Display and Interactive Assessment', layout)

while True:
    event, values = window.read()
    if event in [sg.WINDOW_CLOSED, 'Exit']:
        break

    if event == 'Apply':
        function_col = values['-FUNC-']
        argument_cols = values['-ARGS-']
        assessment = values['-ASSESS-']

        if not function_col or not argument_cols:
            sg.popup_error("Please select both a function and its arguments.")
            continue

        # Placeholder: Replace with your multi-criteria assessment logic
        # Generate new data for TABLE2 based on selections
        new_data_list = [[f"Alt {i+1}" for _ in range(len(headers))] for i in range(5)]

        window['-TABLE2-'].update(values=new_data_list)

window.close()
