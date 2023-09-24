import PySimpleGUI as sg
import json
import os
from datetime import datetime

# Starting layout for choosing or creating a project
starting_layout = [
    [sg.Text("Welcome to the Multi-criteria Assessment App")],
    [sg.Button("Create New Project")],
    [sg.InputText(key='-FILE_PATH-', visible=False, enable_events=True), sg.FileBrowse("Load Existing Project", target='-FILE_PATH-', file_types=(("JSON Files", "*.json"),))],
    [sg.Button("Proceed", visible=False, key='-LOAD_PROJECT-'), sg.Exit()]
]

# Layout for adding alternatives
prepare_alternatives_layout = [
    [sg.Text("Input alternatives as raw data:")],
    [sg.Multiline(size=(40, 10), key='raw_data')],
    [sg.Text("Initialize database file:")],
    [sg.InputText(key='db_file'), sg.FileBrowse()],
    [sg.Text("Pick a function:")],
    [sg.Combo(['Function 1', 'Function 2'], key='function')],
    [sg.Text("Arguments:")],
    [sg.InputText(key='args'), sg.Button("Add Arg"), sg.Button("Delete Arg")],
    [sg.Button("Submit Alternatives")]
]

# Layout for sorting alternatives
sort_alternatives_layout = [
    [sg.Text("Pick sorting method:")],
    [sg.Combo(['Method 1', 'Method 2'], key='sort_method')],
    [sg.Text("Sort specifics (if any):")],
    [sg.InputText(key='sort_specifics')],
    [sg.Checkbox('Sort out non-pareto-optimal', key='pareto')],
    [sg.Button("Rank Alternatives")]
]

# Layout for the results
results_layout = [
    [sg.Text("List of methods used:")],
    [sg.Multiline(size=(40, 5), key='methods_used')],
    [sg.Text("Preferred Alternatives:")],
    [sg.Multiline(size=(40, 10), key='preferred_alts')]
]

# Combine everything
main_layout = [
    [sg.TabGroup([
        [sg.Tab('Prepare Alternatives', prepare_alternatives_layout),
         sg.Tab('Sort Alternatives', sort_alternatives_layout),
         sg.Tab('Results', results_layout)]
    ])],
    [sg.Exit()]
]

# Create the starting window
window = sg.Window("Choose or Create a Project", starting_layout)

# Main event loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == '-FILE_PATH-':
        # Trigger the '-LOAD_PROJECT-' event when a file is chosen
        window.write_event_value('-LOAD_PROJECT-', '')
    elif event == "Create New Project":
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        project_name = f"Project_{current_time}"
        project_filename = f"{project_name}.json"

        with open(project_filename, "w") as f:
            json.dump({"name": project_name, "alternatives": [], "methods": []}, f)
        
        print(f"Created new project: {project_name}")
        
        # Switch to the main assessment window
        window.close()
        window = sg.Window("Multi-criteria Assessment", main_layout)
    elif event == "-LOAD_PROJECT-":
        project_path = values['-FILE_PATH-']
        if project_path and os.path.exists(project_path):
            print(f"Loading existing project from: {project_path}")
            with open(project_path, "r") as f:
                project_data = json.load(f)
            
            # Switch to the main assessment window
            window.close()
            window = sg.Window("Multi-criteria Assessment", main_layout)
        else:
            sg.popup_error("Project file not found.")

    # Main assessment window event handling
    # Placeholder logic for handling these functionalities
    elif event in ["Submit Alternatives", "Add Arg", "Delete Arg", "Rank Alternatives"]:
        sg.popup(f"{event} functionality to be implemented.")

window.close()
