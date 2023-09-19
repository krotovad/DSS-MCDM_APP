import shelve
import PySimpleGUI as sg

def save_state(values):
    with shelve.open('app_state') as db:
        db['state'] = values

def load_state():
    with shelve.open('app_state') as db:
        return db.get('state', None)

layout = [
    [sg.Text('Your name:'), sg.Input(key='-NAME-')],
    [sg.Text('Your age:'), sg.Input(key='-AGE-')],
    [sg.Button('Save'), sg.Button('Load'), sg.Button('Exit')]
]

# Create the window with finalize=True
window = sg.Window('Save and Restore Example with Shelve', layout, finalize=True)

# Load previous state
initial_values = load_state()
if initial_values:
    window.fill(initial_values)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    if event == 'Save':
        save_state(values)
    if event == 'Load':
        new_values = load_state()
        if new_values:
            window.fill(new_values)

window.close()
