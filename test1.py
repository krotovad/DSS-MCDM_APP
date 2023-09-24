import PySimpleGUI as sg
import os

layout = [
    [sg.Text("Choose a File:")],
    [sg.InputText(key='-FILE_PATH-', visible=False), sg.FileBrowse("Browse", target='-FILE_PATH-', file_types=(("JSON Files", "*.json"),))],
    [sg.Exit()]
]

window = sg.Window("File Browser Test", layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        file_path = values['-FILE_PATH-']
        if file_path and os.path.exists(file_path):
            print(f"File selected: {file_path}")
        else:
            print("No file selected or file does not exist.")
        break

window.close()
