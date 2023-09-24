import PySimpleGUI as sg

# Styling
button_color = ('white', '#007899')
border_width = 1
font = ("Helvetica", 12)
button_size = (25, 3)

# Define the layout
layout = [
    [
        sg.Button("Calculate Alternatives", button_color=button_color, border_width=border_width, font=font, size=button_size, key='CALCULATE_BUTTON'),
        sg.Button("Input Alternatives", button_color=button_color, border_width=border_width, font=font, size=button_size, key='INPUT_BUTTON'),
        sg.Button("Multicriterial Assessment", button_color=button_color, border_width=border_width, font=font, size=button_size, disabled=True, key='ASSESSMENT_BUTTON')
    ]
]

def CalculateAlternativesWindow():
    layout = [
        [sg.Button("Save"), sg.Button("Cancel")]
    ]

    window = sg.Window("Calculate Alternatives", layout)
    save_pressed = False

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Cancel"):
            break
        elif event == "Save":
            print("Save pressed in Calculate Alternatives window")
            save_pressed = True
            break

    window.close()
    return save_pressed

def InputAlternativesWindow():
    data = [['' for _ in range(3)] for _ in range(3)]  # initial 3x3 data
    
    def create_layout():
        # Create headings
        headings = ['FUNCTION'] + [f'CRITERIA {i}' for i in range(1, len(data[0]))]
        
        # Initialize table data with headings
        table_data = [['' for _ in range(len(headings))] for _ in range(len(data))]
        
        # Layout
        layout = [
            [sg.Button("Import from CSV", key="-IMPORT_CSV-"), sg.Button("Import from XLSX", key="-IMPORT_XLSX-"),
             sg.Button("Add Column", key="-ADD_COLUMN-"), sg.Button("Add Row", key="-ADD_ROW-")],
            [sg.Table(values=table_data, headings=headings, display_row_numbers=True, auto_size_columns=True,
                      num_rows=min(25, len(table_data)), key='-TABLE-', row_height=25, justification='center',
                      enable_events=True, enable_click_events=True)],
            [sg.Button("Save", key="-SAVE-"), sg.Button("Cancel", key="-CANCEL-")]
        ]
        
        return layout
    
    window = sg.Window("Input Alternatives", create_layout(), resizable=True, finalize=True)
    
    while True:
        event, values = window.read()
        
        if event in (sg.WINDOW_CLOSED, "-CANCEL-"):
            break
        elif event == "-SAVE-":
            # Process the saved data
            window.close()
            return True
        elif event == "-ADD_COLUMN-":
            for row in data:
                row.append('')
            window.close()
            window = sg.Window("Input Alternatives", create_layout(), resizable=True, finalize=True)
        elif '+CLICKED+' in event:
            sg.popup("You clicked row:{} Column: {}".format(event[2][0], event[2][1]))
        elif event == "-ADD_ROW-":
            new_row = ['' for _ in range(len(data[0]))]
            data.append(new_row)
            window.close()
            window = sg.Window("Input Alternatives", create_layout(), resizable=True, finalize=True)
    
    window.close()

def AssessmentWindow():
    layout = [
        [sg.Text("Assessment Window")],  # This window is just for demo purposes, you can add the real layout later.
        [sg.Button("Exit")]
    ]

    window = sg.Window("Multicriterial Assessment", layout)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

    window.close()

# Initialize the Window
window = sg.Window("Main Layout", layout)

# Event Loop
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'CALCULATE_BUTTON':
        print("Calculating Alternatives...")
        save_pressed = CalculateAlternativesWindow()
        if save_pressed:
            window['ASSESSMENT_BUTTON'].update(disabled=False)
    elif event == 'INPUT_BUTTON':
        print("Inputting Alternatives...")
        save_pressed = InputAlternativesWindow()
        if save_pressed:
            window['ASSESSMENT_BUTTON'].update(disabled=False)
    elif event == 'ASSESSMENT_BUTTON':
        print("Performing Multicriterial Assessment...")
        AssessmentWindow()

window.close()