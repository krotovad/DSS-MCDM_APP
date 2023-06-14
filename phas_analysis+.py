import csv
import math
import PySimpleGUI as sg


def dist(x2, y2, x1, y1):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))


def save_element_as_file(element, filename):
    widget = element.Widget
    box = (widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_rootx() + widget.winfo_width(),
           widget.winfo_rooty() + widget.winfo_height())
    grab = ImageGrab.grab(bbox=box)
    grab.save(filename)


def draw_axis(graph, xmin, xmax, ymin, ymax, step_y, step_x):
    graph.draw_line((xmin, ymin), (xmin, ymax))
    graph.draw_line((xmin, ymin), (xmax, ymin))
    stepY = (ymax - ymin) // step_y
    for x in range(xmin, xmax, step_x):
        graph.draw_line((x, ymin), (x, ymin - (ymax - ymin) / 50))
        if x != 0:
            graph.draw_text(str(x), (x, ymin - (ymax - ymin) / 40), color='green')

    for y in range(ymin, ymax, stepY):
        graph.draw_line((xmin - step_x / 5, y), (xmin, y))
        if y != 0:
            graph.draw_text(str(y), (xmin - step_x, y), color='blue')


num_cols = 3
data = []

start_layout = [[sg.Button("Ввод данных", k='input')],
                [sg.Button("Общий график", k='graphset', disabled=True)],
                [sg.Button("Определение квазициклов", k='graph', disabled=True)],
                [sg.Button("Анализ квазициклов", k='stats', disabled=True)]]
start_window = sg.Window("Фазовый анализ", start_layout, size=(300, 150))
while True:
    start_event, start_values = start_window.read()
    if start_event == 'input':
        start_window.Hide()

        file_browser_layout = [[sg.Radio("Заголовки есть", group_id='headerCheck', default=True),
                                sg.Radio("Заголовков нет", group_id='headerCheck', k='noHead')],
                               [sg.Text("Разделитель "), sg.Combo(values=[',', ';', 'space', 'tab'], key="combo")],
                               [sg.Input(key="path", disabled=True),
                                sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
                                sg.Button("OK", key="submit")]]
        file_browser = sg.Window('Выберите файл', file_browser_layout)
        while True:
            br_event, br_values = file_browser.read()

            if br_event == "submit":
                path = str(br_values["path"])
                sep = br_values["combo"]
                if path == '':
                    sg.PopupError('Файл не выбран')
                elif sep == '':
                    sg.PopupError('Разделитель не выбран')
                else:
                    file_browser.Hide()
                    with open(path, "r") as csv_file:
                        csv_reader = csv.DictReader(csv_file, delimiter=sep)
                        rows = list(csv_reader)
                        num_rows = len(rows)

                        if br_values['noHead']:
                            header_list = ['Столбец ' + str(i) for i in range(len(csv_reader.fieldnames))]
                        else:
                            header_list = csv_reader.fieldnames
                        data = [["" for j in range(num_cols)] for i in range(num_rows)]

                    specs_layout = [[sg.Text("Столбец данных"), sg.Combo(header_list, key='data')],
                                    [sg.Text("Столбец характеристики"), sg.Combo(header_list, key='factor')],
                                    [sg.Button('OK', key='submit')]]
                    specs_window = sg.Window('Выбор данных', specs_layout)

                    while True:
                        specs_event, specs_values = specs_window.read()
                        if specs_event == 'submit':
                            data_col = specs_values['data']
                            factor_col = specs_values['factor']
                            if data_col == '' or factor_col == '':
                                sg.PopupError('Не все cтолбцы данных выбраны')
                            else:
                                file_browser.close()
                                header_list = [factor_col, data_col, 'Сдвиг']
                                specs_window.close()
                                start_window['graphset'].Update(disabled=False)
                                start_window['graph'].Update(disabled=True)
                                start_window['stats'].Update(disabled=True)
                                start_window.UnHide()
                                i = 0
                                x_min = float(rows[0][data_col])
                                x_max = float(rows[0][data_col])
                                y_min = float(rows[1][data_col])
                                y_max = float(rows[1][data_col])

                                for line in rows:
                                    data[i][0] = line[factor_col]
                                    data[i][1] = float(line[data_col])
                                    if i == num_rows - 1:
                                        data[i][2] = None
                                    else:
                                        data[i][2] = float(rows[i + 1][data_col])
                                        if data[i][1] > x_max: x_max = data[i][1]
                                        if data[i][1] < x_min: x_min = data[i][1]
                                        if data[i][2] > y_max: y_max = data[i][2]
                                        if data[i][2] < y_min: y_min = data[i][2]
                                    i += 1
                                break

                        if specs_event == sg.WINDOW_CLOSED:
                            specs_window.close()
                            file_browser.UnHide()
                            break

            if br_event == sg.WINDOW_CLOSED:
                file_browser.close()
                start_window.UnHide()
                break

    if start_event == 'graphset':
        start_window.Hide()

        graphsNav = []
        graphHeadings = ['Начальный индекс', 'Конечный индекс', 'L м/у концами', 'N точек']

        for i in range(num_rows - 15):
            pointer = 0
            temp = []
            for j in range(i + 3, i + 15):
                currdist = dist(data[j][1], data[j][2], data[i][1], data[i][2])
                temp.append(currdist)
            mindist = min(temp)
            pointer = temp.index(min(temp)) + 3
            graphsNav.append([i, pointer + i, float("%.3f" % mindist), pointer + 1])

        graph = sg.Graph(canvas_size=(700, 700),
                         background_color="white",
                         graph_bottom_left=(int(x_min) - int(x_max - x_min) // 10, - int(y_max - y_min) // 10),
                         graph_top_right=(int(x_max) + int(x_max - x_min) // 10, int(y_max) + int(y_max - y_min) // 10),
                         key='og_graph')

        graphset_layout = [[sg.Table(values=data, key="table", background_color="white", headings=header_list,
                                     display_row_numbers=True, num_rows=25, auto_size_columns=True,
                                     justification="center", text_color="black"),
                            graph,
                            sg.Table(values=graphsNav, key="graphstable", background_color="white",
                                     headings=graphHeadings,
                                     display_row_numbers=False, num_rows=25, auto_size_columns=True,
                                     justification="center", text_color="black")],
                           [sg.Text('Текущее количество точек'), sg.Text('Н/Д', key='pointsum')],
                           [sg.Button("Увеличить", key='inc'), sg.Button("Уменьшить", key='dec', disabled=True),
                            sg.Button("Максимум", key='tomax')],
                           [sg.Button(button_text="Отобразить выбранное количество значений", key='setgraph')],
                           [sg.Button(button_text="Назад", key='return'), sg.Button('Сохранить график', key='export')]]

        graphset_window = sg.Window("Отображение выбранных данных", graphset_layout)
        pointsum = 0
        while True:
            graph_event, graph_values = graphset_window.read()

            if graph_event == 'setgraph':
                graph.erase()
                for i in range(pointsum):
                    graph.draw_line((float(data[i][1]), float(data[i][2])),
                                    (float(data[i + 1][1]), float(data[i + 1][2])))

            if graph_event == 'inc':
                pointsum = pointsum + 1
                if pointsum == num_rows - 2:
                    graphset_window['inc'].Update(disabled=True)
                if pointsum == 1:
                    graphset_window['dec'].Update(disabled=False)
                graphset_window['pointsum'].Update(value=str(pointsum))

            if graph_event == 'tomax':
                pointsum = num_rows - 2
                graphset_window['inc'].Update(disabled=True)
                graphset_window['dec'].Update(disabled=False)
                graphset_window['pointsum'].Update(value=str(pointsum))

            if graph_event == 'dec':
                if pointsum == 1:
                    graphset_window['dec'].Update(disabled=True)
                if pointsum == num_rows - 2:
                    graphset_window['inc'].Update(disabled=False)
                pointsum = pointsum - 1
                graphset_window['pointsum'].Update(value=str(pointsum))

            if graph_event == 'export':
                try:
                    filename = sg.popup_get_file('Выберите файл', save_as=True, file_types=(("PNG Files", "*.png"),))
                    save_element_as_file(graphset_window['og_graph'], filename)
                except ValueError:
                    sg.PopupError('Файл не выбран')
            if graph_event == sg.WINDOW_CLOSED or graph_event == 'return':
                graphset_window.close()
                start_window['graph'].Update(disabled=False)
                start_window.UnHide()
                break

    if start_event == sg.WIN_CLOSED:
        start_window.close()
        break

    if start_event == 'graph':
        graphNum = "Н/Д"

        cycleHead = ['Начальный фактор', 'Конечный фактор', 'Площадь', 'Центр']
        cycles = []
        cyclesIter = []

        pos = 0
        while True:
            if graphsNav[pos + 1][2] > graphsNav[pos][2]:
                break
            else:
                pos = pos + 1

        while True:
            if pos > len(graphsNav) - 12:
                break
            elif graphsNav[pos][1] < len(data):
                iterStart = int(graphsNav[pos][0])
                iterEnd = int(graphsNav[pos][1])
                distStart = dist(data[iterStart][1],data[iterStart][2], 0, 0)
                distEnd = dist(data[iterEnd][1],data[iterEnd][2], 0, 0)
                print(iterStart, iterEnd, distStart, distEnd, graphsNav[pos][2])
                if graphsNav[pos][2] <= 15 % (max(distStart, distEnd)):
                    tempX = []
                    tempY = []
                    for i in range(iterStart, iterEnd):
                        tempX.append(data[int(graphsNav[i][0])][1])
                        tempY.append(data[int(graphsNav[i][1])][2])
                    minX = min(tempX)
                    maxX = max(tempX)
                    minY = min(tempY)
                    maxY = max(tempY)
                    space = float("%.3f" % ((maxX - minX) * (maxY - minY)))
                    center = [float("%.3f" % ((minX + maxX) / 2)), float("%.3f" % ((minY + maxY) / 2))]
                    cyclesIter.append([graphsNav[pos][0], graphsNav[pos][1]])
                    cycles.append([data[graphsNav[pos][0]][0], data[graphsNav[pos][1]][0], space, center])
                pos = graphsNav[pos][1] + 1
        single_graph = sg.Graph(canvas_size=(700, 700),
                                background_color="white",
                                graph_bottom_left=(int(x_min) - 10, int(y_min) - 10),
                                graph_top_right=(int(x_max) + 10, int(y_max) + 10),
                                key='single_graph')

        single_layout = [[sg.Text('Номер квазицикла: '), sg.Text(graphNum, key='graphNum')],
                         [sg.Table(values=cycles, key="graphstable", background_color="white",
                                   headings=cycleHead,
                                   display_row_numbers=False, num_rows=25, auto_size_columns=True,
                                   justification="center", text_color="black"),
                          single_graph],
                         [sg.Button(button_text="Отобразить следующий цикл", key='next'),
                          sg.Button(button_text="Отобразить предыдущий цикл", key='prev', disabled=True)],
                         [sg.Button(button_text="Назад", key='return'), sg.Button('Сохранить график', key='export')]]
        start_window.Hide()
        single_window = sg.Window("Графики квазициклов", single_layout)
        pos = -1
        while True:
            single_event, single_values = single_window.read()
            if single_event == "next":
                single_graph.erase()
                pos = pos + 1
                for j in range(cyclesIter[pos][0], cyclesIter[pos][1]):
                    single_graph.draw_line(((float(data[j][1])), float(data[j][2])),
                                           (float(data[j + 1][1]), float(data[j + 1][2])))
                single_window['graphNum'].Update(value=str(pos + 1))
                if pos > 0: single_window['prev'].Update(disabled=False)
                if pos == len(cyclesIter) - 1: single_window['next'].Update(disabled=True)
            if single_event == "prev":
                single_graph.erase()
                pos = pos - 1
                for j in range(cyclesIter[pos][0], cyclesIter[pos][1]):
                    single_graph.draw_line(((float(data[j][1])), float(data[j][2])),
                                           (float(data[j + 1][1]), float(data[j + 1][2])))
                single_window['graphNum'].Update(value=str(pos + 1))
                if pos == 0: single_window['prev'].Update(disabled=True)
                if pos < len(cyclesIter): single_window['next'].Update(disabled=False)
            if single_event == 'export':
                try:
                    filename = sg.popup_get_file('Выберите файл', save_as=True, file_types=(("PNG Files", "*.png"),))
                    save_element_as_file(single_window['single_graph'], filename)
                except ValueError:
                    sg.PopupError('Файл не выбран')
            if single_event == sg.WINDOW_CLOSED or single_event == 'return':
                single_window.close()
                start_window['stats'].Update(disabled=False)
                start_window.UnHide()
                break
    if start_event == 'stats':
        spaceArr = []
        centersX = []
        centersY = []
        for i in range(len(cycles)):
            spaceArr.append(float(cycles[i][2]))
        s_min = min(spaceArr)
        s_max = max(spaceArr)

        for i in range(len(cycles)):
            temp = cycles[i][3]
            centersX.append(temp[0])
            centersY.append(temp[1])
        c_minX = min(centersX)
        c_maxX = max(centersX)
        c_minY = min(centersY)
        c_maxY = max(centersY)

        stats_graph = sg.Graph(canvas_size=(1400, 700),
                               background_color="white",
                               graph_bottom_left=(-2, int(s_min) - int((s_max - s_min) / 10)),
                               graph_top_right=(int(len(spaceArr)), int(s_max) + int((s_max - s_min) / 10)),
                               enable_events=True,
                               key='stats_graph')
        centers_graph = sg.Graph(canvas_size=(1400, 700),
                                 background_color="white",
                                 graph_bottom_left=(
                                     int(c_minX) - int((c_maxX - c_minX) / 10),
                                     int(c_minY) - int((c_maxY - c_minY) / 10)),
                                 graph_top_right=(
                                     int(c_maxX) + int((c_maxX - c_minX) / 10),
                                     int(c_maxY) + int((c_maxY - c_minY) / 10)),
                                 enable_events=True,
                                 key='centers_graph')
        tab_space = [[sg.Text('Эволюция площадей габаритных прямоугольников')],
                     [stats_graph],
                     [sg.Button('Назад', key='returnS'),
                      sg.Button('Сохранить график', key='export_s')]]
        tab_centers = [[sg.Text('Движение центров квазициклов')],
                       [centers_graph],
                       [sg.Button('Назад', key='returnC'),
                        sg.Button('Сохранить график', key='export_c')]]
        stats_layout = [[sg.TabGroup([[sg.Tab('Площади', tab_space), sg.Tab('Центры', tab_centers)]])]]
        stats_window = sg.Window('Эволюция площадей', stats_layout, finalize=True)
        for i in range(len(spaceArr) - 1):
            stats_graph.draw_line(((float(i)), float(spaceArr[i])),
                                  (float(i + 1), float(spaceArr[i + 1])))
        draw_axis(stats_graph, 0, len(spaceArr), int(s_min), int(s_max), 6, 1)
        for i in range(len(centersX) - 1):
            centers_graph.draw_line(((float(centersX[i])), float(centersY[i])),
                                    (float(centersX[i + 1]), float(centersY[i + 1])))
        draw_axis(centers_graph, int(c_minX), int(c_maxX), int(c_minY), int(c_maxY), 6, 10)
        while True:
            stats_event, stats_values = stats_window.read()
            if stats_event == 'export_c':
                try:
                    filename = sg.popup_get_file('Выберите файл', save_as=True, file_types=(("PNG Files", "*.png"),))
                    save_element_as_file(stats_window['centers_graph'], filename)
                except ValueError:
                    sg.PopupError('Файл не выбран')
            if stats_event == 'export_s':
                try:
                    filename = sg.popup_get_file('Выберите файл', save_as=True, file_types=(("PNG Files", "*.png"),))
                    save_element_as_file(stats_window['stats_graph'], filename)
                except ValueError:
                    sg.PopupError('Файл не выбран')
            if stats_event == 'returnS' or stats_event == 'returnC' or stats_event == sg.WINDOW_CLOSED:
                stats_window.close()
                start_window.UnHide()
                break