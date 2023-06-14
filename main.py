import PySimpleGUI as sg

start_layout = [[sg.Button("Ввод данных", k='input')],
                [sg.Button("Общий график", k='graphset', disabled=True)],
                [sg.Button("Определение квазициклов", k='graph', disabled=True)],
                [sg.Button("Анализ квазициклов", k='stats', disabled=True)]]
start_window = sg.Window("Фазовый анализ", start_layout, size=(300, 150))
while True:
    start_event, start_values = start_window.read()