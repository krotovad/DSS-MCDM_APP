import csv
import sys
import openpyxl
import sqlite3
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

method_descriptions = {
    'MINSUM': {
        'description': (
        'Минимальная сумма (MINSUM)\n'
        '-------------------\n'
        '- Подход: Агрегирует оценки альтернатив на основе суммы их баллов, отдавая предпочтение альтернативам с наименьшим суммарным баллом.\n'
        '- Исходные данные: Требуется матрица оценок, состоящая из m альтернатив и n критериев.\n'
        '- Выходные данные: Одна предпочтительная альтернатива.\n'
        '- Идеально подходит для: Задачи, в которых лицо, принимающее решение, предпочитает минимизировать совокупные оценки, подходит для задач минимизации затрат.'
        ),
        'args': [
            
        ]
    },
    'MINMAX': {
        'description': (
        'Минимум-Максимум (MINMAX)\n'
        '-----------------------\n'
        '- Подход: Выбирается альтернатива, которая имеет наименьшее максимальное значение, минимизируя наихудший исход.\n'
        '- Исходные данные: Требуется матрица оценки, состоящая из m альтернатив и n критериев.\n'
        '- Выходные данные: Одна предпочтительная альтернатива.\n'
        '- Идеально подходит для: Ситуации принятия решений, когда избежание риска имеет решающее значение, и лицо, принимающее решение, хочет избежать наихудшего возможного исхода.'
        ),
        'args': [
            
        ]
    },
    'MAXMIN': {
        'description': (
        'Максимум-Минимум (MAXMIN)\n'
        '-----------------------\n'
        '- Подход: Выбирается альтернатива, имеющая наибольшее минимальное значение, максимизирующая наихудший исход.\n'
        '- Исходные данные: Требуется матрица оценки, состоящая из m альтернатив и n критериев.\n'
        '- Выходные данные: Одна предпочтительная альтернатива.\n'
        '- Идеально подходит для: Сценарии, ориентированные на извлечение наибольшей выгоды из наименее благоприятных условий, пригодные для анализа устойчивости.'
        ),
        'args': [
            
        ]
    }, 'TOPSIS': {
        'description': (
            'Техника упорядочивания предпочтений по сходству с идеальным решением (TOPSIS)\n'
            '-----------------------------------------\n'
            '- Подход: Сравнивает каждую альтернативу с теоретически идеальным решением.\n'
            '- Исходные данные: Требуется матрица оценки, состоящая из m альтернатив и n критериев.\n'
            '- Выходные данные: Ранжирование альтернатив.\n'
            '- Идеально подходит для: Задачи, в которых необходимо выбрать лучшую альтернативу из заданного множества.'
        ),
        'args': [
            {
                'name': 'Weights',
                'type': 'multiple',
                'applies_to': 'each_criteria'
            },
        ]
    },
    'WSR': {
        'description': (
            'Weighted Sum Model (WSM) или Weighted Linear Combination\n'
            '----------------------------------------------------\n'
            '- Подход: Присваивает веса в зависимости от важности каждого критерия.\n'
            '- Входы: Баллы каждой альтернативы по каждому критерию.\n'
            '- Выходные данные: Единая общая оценка для каждой альтернативы.\n'
            '- Идеально подходит для: Ситуации, когда возможны компромиссы между критериями.'
        ),
        'args': [
            {
                'name': 'Weights',
                'type': 'multiple',
                'applies_to': 'each_criteria'
            },
            # При необходимости добавьте другие аргументы
        ]
    },
    'ELECTRE': {
        'description': (
            'Elimination Et Choix Traduisant la Realité (ELECTRE)\n'
            '---------------------------------------------------\n'
            '- Подход: Исключает альтернативы, которые не соответствуют определенным критериям.\n'
            '- Исходные данные: Таблица характеристик, состоящая из характеристик каждой альтернативы по каждому критерию.\n'
            '- Выходные данные: Частичный предварительный порядок альтернатив.\n'
            '- Идеально подходит для: Задачи с противоречивыми критериями, где требуется набор всех потенциально хороших решений.'
        ),
        'args': [
            {
                'name': 'Concordance Threshold',
                'type': 'singular',
                'applies_to': 'all'
            },
            {
                'name': 'Discordance Threshold',
                'type':'singular',
                'applies_to': 'all'
            },
            # При необходимости добавьте другие аргументы
        ]
    },
    'VIKOR': {
        'description': (
            'VlseKriterijumska Optimizacija I Kompromisno Resenje (VIKOR)\n'
            '----------------------------------------------------------\n'
            '- Подход: Представляет многокритериальный ранжирующий индекс, основанный на конкретной мере "близости" к "идеальному" решению.\n'
            '- Исходные данные: Матрица оценок альтернатив по всем критериям.\n'
            '- Выходные данные: Компромиссное решение и список ранжирования.\n'
            '- Идеально подходит для: Общественные проблемы принятия решений, особенно для решения проблемы распределения водных ресурсов.'
        ),
        'args': [
            {
                'name': 'Weights',
                'type': 'multiple',
                'applies_to': 'each_criteria'
            },
        ]
    }
}

class ResultsWindow(QWidget):
    def __init__(self, data, methods, inputs, parent=None):
        super(ResultsWindow, self).__init__(parent)
        
        self.data = data  # Original data
        self.methods = methods
        self.inputs = inputs
        self.is_pareto = False  # Flag to check whether to show Pareto front or original data
        
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout()
        data_display_layout = QHBoxLayout()
        
        # 1. Display Data        
        self.data_table = QTableWidget()
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setDataTable()  # Set the table data when the window is loaded
        data_display_layout.addWidget(self.data_table, 1)
        
        # 2. Results section
        results_layout = QHBoxLayout()

        self.tabs = QTabWidget()

        for method in self.methods:
            tab = QWidget()
            tab_layout = QHBoxLayout(tab)  # Assign the layout directly to the tab

            results_table = QTableWidget()
            self.update_results(results_table, method)  # Assuming you'll write this function later

            tab_layout.addWidget(results_table)  # Add the table to the left of the layout
            # Here, you can add additional widgets to the tab_layout if needed
            
            tab.setLayout(tab_layout)  # Set the layout for the tab
            self.tabs.addTab(tab, method)  # Add the tab to the QTabWidget

        results_layout.addWidget(self.tabs, 1)
                       
        self.pareto_button = QPushButton("Сортировка по Парето")
        self.pareto_button.clicked.connect(self.toggle_pareto)

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.clicked.connect(self.close)
        
        main_layout.addLayout(data_display_layout, 1)
        main_layout.addLayout(results_layout, 1)
        main_layout.addWidget(self.pareto_button)
        main_layout.addWidget(self.cancel_button)
        self.setLayout(main_layout)
        
    def toggle_pareto(self):       
        self.is_pareto = not self.is_pareto  # Toggle the state
        if self.is_pareto:
            self.pareto_button.setText("Данные AS-IS")            
        else:
            self.pareto_button.setText("Сортировка по Парето")
        self.setDataTable()  # Update the table according to the new state
        tabs = self.tabs  # Assuming this is your QTabWidget instance

        for index in range(tabs.count()):  # Iterating over all tabs
            tab = tabs.widget(index)  # Getting the QWidget instance representing the tab
            title = tabs.tabText(index)            
            layout = tab.layout()  # Getting the layout of the tab. Assuming there is a layout.
            
            # Iterate over all widgets in the layout to find QTableWidget instances
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                
                if isinstance(widget, QTableWidget):  # Checking if the widget is a QTableWidget
                    # Now 'widget' refers to the QTableWidget instance in the current tab.
                    # You can perform your operations on this table widget instance.
                    self.update_results(widget, title)
    
    def setDataTable(self):
        data = self.pareto_dominance(self.data) if self.is_pareto else self.data  # Choose data according to the state
        row_count = len(data)
        col_count = len(data[0])
        self.data_table.setRowCount(row_count)
        self.data_table.setColumnCount(col_count)
        
        for row_index, row_data in enumerate(data):
            for col_index, cell_data in enumerate(row_data):
                self.data_table.setItem(row_index, col_index, QTableWidgetItem(str(round(cell_data,3))))
                
    def read_table_data(self, data_table):
        rows = data_table.rowCount()
        cols = data_table.columnCount()
        data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = data_table.item(row, col)
                if item and item.text():
                    row_data.append(float(item.text()))  # assuming all cells contain numeric data
            data.append(row_data)
        return data

    
    def pareto_dominance(self, data):
        if not data or not isinstance(data, list) or len(data) < 2:
            return []
        
        pareto_front = []
        for i, alt1 in enumerate(data):
            dominated = False
            for j, alt2 in enumerate(data):
                if i != j:
                    if all(a >= b for a, b in zip(alt1, alt2)) and any(a > b for a, b in zip(alt1, alt2)):
                        dominated = True
                        break
            if not dominated:
                pareto_front.append(alt1)
        return pareto_front

    def update_results(self, results_table, method):
        # Make a dictionary of method names and their corresponding functions
        methods_dict = {
            "MINSUM": self.minsum,
            "MINMAX": self.minmax,
            "MAXMIN": self.maxmin,
            "TOPSIS": self.topsis
            # Add other methods as needed
        }
        
        # Call the appropriate method and get the results
        method_name = method.upper()  # Convert method name to upper case to match the keys in methods_dict
        if method_name in methods_dict:
            results = methods_dict[method_name]()
            results = [[row[0]] + [round(val, 3) if isinstance(val, float) else val for val in row[1:]] for row in results]
        else:
            print(f"Method {method_name} not found.")
            return
        
        # Now, fill the results_table with the results obtained from the method call
        row_count = len(results)
        col_count = len(results[0]) if results else 0  # Avoid IndexError in case results is an empty list
        
        results_table.setRowCount(row_count)
        results_table.setColumnCount(col_count)
        
        for row_index, row_data in enumerate(results):
            for col_index, col_data  in enumerate(row_data):
                results_table.setItem(row_index, col_index, QTableWidgetItem(str(round(col_data, 3))))

    def minsum(self):
        data = self.read_table_data(self.data_table)
        minsum_list = []
        for row in data:
            sum_value = sum(row)
            minsum_list.append([sum_value] + row)
        minsum_list.sort(key=lambda x: x[0])
        return minsum_list

    def minmax(self):
        data = self.read_table_data(self.data_table)
        minmax_list = []
        for row in data:
            minmax_value = max(row)
            minmax_list.append([minmax_value] + row)
        minmax_list.sort(key=lambda x: x[0])
        return minmax_list


    def maxmin(self):
        data = self.read_table_data(self.data_table)
        maxmin_list = []
        for row in data:
            maxmin_value = min(row)
            maxmin_list.append([maxmin_value] + row)
        maxmin_list.sort(key=lambda x: x[0], reverse=True)
        return maxmin_list


    def topsis(self):
        data = self.read_table_data(self.data_table)
        weights = [float(weight) for weight in self.inputs]

        normalized_decision_matrix = []
        for col in range(len(data[0])):
            column = [row[col] for row in data]
            norm = (sum(x ** 2 for x in column)) ** 0.5
            normalized_decision_matrix.append([x / norm for x in column])

        weighted_normalized_decision_matrix = [[val * weights[i] for val in col] for i, col in enumerate(normalized_decision_matrix)]
        ideal_solution = [max(col) for col in weighted_normalized_decision_matrix]
        negative_ideal_solution = [min(col) for col in weighted_normalized_decision_matrix]

        separation_measures = []
        for row in range(len(data)):
            s_positive = sum((weighted_normalized_decision_matrix[col][row] - ideal_solution[col]) ** 2 for col in range(len(ideal_solution))) ** 0.5
            s_negative = sum((weighted_normalized_decision_matrix[col][row] - negative_ideal_solution[col]) ** 2 for col in range(len(negative_ideal_solution))) ** 0.5
            separation_measures.append((s_negative / (s_positive + s_negative),) + tuple(data[row]))

        ranked_alternatives = sorted(separation_measures, key=lambda x: x[0], reverse=True)
        return ranked_alternatives

    def electre(data):
        # This is a placeholder. ELECTRE usually involves a more complex procedure with concordance and discordance indices, thresholds, etc.
        return [sum(alternative[1:]) for alternative in data]  # placeholder, please replace with actual implementation

    def vikor(data):
        # This is a placeholder. VIKOR usually involves more complex computations including weighting, utility, and regret measures.
        return [sum(alternative[1:]) for alternative in data]  # placeholder, please replace with actual implementation

class AssessmentWindow(QWidget):
    def __init__(self, data):
        super(AssessmentWindow, self).__init__()
        self.data = data
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1300, 600)
        self.setWindowTitle('Определение настроек оценки')
        self.selected_methods = []
        self.additional_inputs = {}

        grid_layout = QGridLayout(self)

        # 1. Section for List of Multicriterial Assessment Methods
        self.method_group = QGroupBox("Методы многокритериальной оценки")
        self.method_list = QListWidget(self.method_group)

        categories_methods = {
            'Примитивы': ['MINSUM', 'MINMAX', 'MAXMIN'],
            'Методы принятия решений': ['TOPSIS', 'WSR'],
            'Методы анализа предпочтений': ['ELECTRE'],
            'Методы установления компромиссов': ['VIKOR']
        }

        for category, methods in categories_methods.items():
            category_item = QListWidgetItem(category)
            category_item.setFlags(Qt.NoItemFlags)
            self.method_list.addItem(category_item)

            for method in methods:
                method_item = QListWidgetItem()
                checkbox = QCheckBox(method)
                self.method_list.addItem(method_item)
                self.method_list.setItemWidget(method_item, checkbox)
                checkbox.stateChanged.connect(self.display_info)

        grid_layout.addWidget(self.method_group, 0, 0)

        # 2. Multiline Widget for Method Info
        self.info_widget = QTextEdit(self)
        font = self.info_widget.font()
        font.setPointSize(12)
        self.info_widget.setFont(font)
        self.info_widget.setPlaceholderText("Здесь отображается информация о выбранных методах")
        grid_layout.addWidget(self.info_widget, 0, 1)


        # 3. Additional Section for Additional Inputs
        self.additional_inputs_group = QGroupBox("Дополнительные параметры")
        self.form_layout = QFormLayout()
        self.input_instruction_label = QLabel()
        self.form_layout.addRow(self.input_instruction_label)
        self.additional_inputs_group.setLayout(self.form_layout)
        grid_layout.addWidget(self.additional_inputs_group, 1, 1)

        
        self.resultsButton = QPushButton("Сохранить и Продолжить")
        self.resultsButton.clicked.connect(lambda: self.showResults(self.data, self.selected_methods, self.read_input_fields()))
        grid_layout.addWidget(self.resultsButton, 2, 1)

        grid_layout.setRowStretch(0, 1)  # Stretch the first row so that it takes up the available space
        grid_layout.setRowStretch(1, 0)  # Do not stretch the second row
        #self.additional_inputs_group.hide()  # Hide by default

        self.method_list.itemSelectionChanged.connect(self.display_info)
        #self.additional_inputs = dict()
        
    def showResults(self, data, methods, inputs):
        #print(data, methods, inputs)    
        self.resultsWindow = ResultsWindow(data, methods, inputs)
        self.resultsWindow.show()
        self.center_on_screen()     
    
    def showEvent(self, event):
        self.center_on_screen()
        super().showEvent(event)

    def center_on_screen(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def read_input_fields(self):
        input_values = []
        for line_edit in self.additional_inputs.values():
            input_value = line_edit.text()
            input_values.append(input_value)
        return input_values

    def display_info(self):
        self.info_widget.clear()
        # Clear previous widgets
        for i in reversed(range(self.form_layout.count())): 
            widget = self.form_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        self.selected_methods = [
            self.method_list.itemWidget(self.method_list.item(i)).text()
            for i in range(self.method_list.count())
            if self.method_list.itemWidget(self.method_list.item(i)) and 
            self.method_list.itemWidget(self.method_list.item(i)).isChecked()
        ]

        if not self.selected_methods:
            self.additional_inputs_group.hide()
            return

        self.additional_inputs.clear()
        
        for method in self.selected_methods:
            self.info_widget.append(method_descriptions[method]['description'])
            if method_descriptions[method]['args']:
                for arg in method_descriptions[method]['args']:
                    self.add_input_field(arg, method)
        
        if self.form_layout.count() > 0:
            self.additional_inputs_group.show()
            #print(f"Additional Inputs Group is Visible: {self.additional_inputs_group.isVisible()}")
        else:
            self.additional_inputs_group.hide()

    def add_input_field(self, arg, method):
        print(self, arg, method)
        name = arg['name']
        arg_type = arg['type']
        applies_to = arg['applies_to']

        if applies_to == 'each_criteria':
            for criterion in range(0, len(self.data[0])):  # Start from 1 to skip the function
                label_str = f"{name} for criterion {criterion} ({method}): "
                line_edit = QLineEdit()
                self.form_layout.addRow(QLabel(label_str), line_edit)
                self.additional_inputs[label_str] = line_edit  # Store the QLineEdit reference
        elif applies_to == 'all':
            if arg_type == 'multiple':
                for criterion in range(0, len(self.data[0])):  # Start from 1 to skip the function
                    label_str = f"{name} for criterion {criterion} ({method}): "
                    line_edit = QLineEdit()
                    self.form_layout.addRow(QLabel(label_str), line_edit)
                    self.additional_inputs[label_str] = line_edit  # Store the QLineEdit reference
            elif arg_type == 'singular':
                label_str = f"{name} ({method}): "
                line_edit = QLineEdit()
                self.form_layout.addRow(QLabel(label_str), line_edit)
                self.additional_inputs[label_str] = line_edit  # Store the QLineEdit reference

class CalculateAlternativesWindow(QDialog):
    def __init__(self):
        super(CalculateAlternativesWindow, self).__init__()

        layout = QVBoxLayout()

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_pressed)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)
        self.save_pressed_flag = False

    def save_pressed(self):
        #print("Save pressed in Calculate Alternatives window")
        self.save_pressed_flag = True
        self.close()

def open_input_alternatives_window(main_window):
    main_window.hide()
    window = InputAlternativesWindow(main_window)
    window.exec_()
    main_window.show()

class InputAlternativesWindow(QDialog):
    def __init__(self):
        super(InputAlternativesWindow, self).__init__()

        self.data = [['' for _ in range(3)] for _ in range(3)]
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        
        # Setup Buttons
        self.setup_buttons()
        
        # Setup Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setRowCount(3)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.itemSelectionChanged.connect(self.handle_item_selection)
        
        # Place the table and button_layout in a horizontal layout
        h_layout = QVBoxLayout()
        h_layout.addLayout(self.button_layout)  # Add button_layout (import and add/remove buttons) to the horizontal layout
        h_layout.addWidget(self.table)  # Add table to the horizontal layout
        
        self.main_layout.addLayout(h_layout)  # Add horizontal layout to the main layout
        self.main_layout.addLayout(self.save_cancel_layout)  # Add save_cancel_layout below the horizontal layout
        
        self.adjust_dialog_size()

    def setup_buttons(self):
        # Create Buttons
        self.import_csv_button = QPushButton("Импорт из CSV", self)
        self.import_xlsx_button = QPushButton("Импорт из XLSX", self)
        self.add_remove_column_button = QPushButton("Добавить столбец", self)
        self.add_remove_row_button = QPushButton("Добавить строку", self)

        # Connect Buttons
        self.import_csv_button.clicked.connect(self.import_csv)
        self.import_xlsx_button.clicked.connect(self.import_xlsx)
        self.add_remove_column_button.clicked.connect(self.add_column)
        self.add_remove_row_button.clicked.connect(self.add_row)

        # Button Layout for import and add/remove buttons
        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.import_csv_button)
        self.button_layout.addWidget(self.import_xlsx_button)
        self.button_layout.addWidget(self.add_remove_column_button)
        self.button_layout.addWidget(self.add_remove_row_button)

        # Save and Cancel Buttons
        self.save_button = QPushButton("Сохранить", self)
        self.cancel_button = QPushButton("Отмена", self)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Button Layout for Save and Cancel
        self.save_cancel_layout = QVBoxLayout()  # Changed to QHBoxLayout to put buttons side by side
        self.save_cancel_layout.addStretch(1)
        self.save_cancel_layout.addWidget(self.save_button)
        self.save_cancel_layout.addWidget(self.cancel_button)


    def adjust_dialog_size(self):
        width = self.table.verticalHeader().width() + 4  # for border
        for i in range(self.table.columnCount()):
            width += self.table.columnWidth(i)  # width of each column

        height = self.table.horizontalHeader().height() + 4
        for i in range(self.table.rowCount()):
            height += self.table.rowHeight(i)  # height of each row

        max_height = 1000  # example value, adjust as needed
        max_width = 2000  # example value, adjust as needed
        
        width = min(width, max_width)
        height = min(height, max_height)
        
        self.resize(width, height)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reset_buttons()
            self.table.clearSelection()
        else:
            super(InputAlternativesWindow, self).keyPressEvent(event)
    
    def mousePressEvent(self, event):
        # Detecting if a widget under the cursor is a QPushButton, if not it's assumed to be empty space
        widget = QApplication.widgetAt(QCursor.pos())
        if not isinstance(widget, QPushButton):
            self.reset_buttons()
            self.table.clearSelection()
        super(InputAlternativesWindow, self).mousePressEvent(event)
    
    def reset_buttons(self):
        self.add_remove_row_button.setText("Добавить строку")
        self.add_remove_row_button.disconnect()
        self.add_remove_row_button.clicked.connect(self.add_row)

        self.add_remove_column_button.setText("Добавить столбец")
        self.add_remove_column_button.disconnect()
        self.add_remove_column_button.clicked.connect(self.add_column)
    
    def handle_item_selection(self):
        selected_indices = self.table.selectedIndexes()
        if selected_indices:
            rows = set(index.row() for index in selected_indices)
            columns = set(index.column() for index in selected_indices)
            if len(rows) == 1:
                self.add_remove_row_button.setText("Удалить строку")
                self.add_remove_row_button.disconnect()
                self.add_remove_row_button.clicked.connect(self.delete_row)
            else:
                self.add_remove_row_button.setText("Добавить строку")
                self.add_remove_row_button.disconnect()
                self.add_remove_row_button.clicked.connect(self.add_row)

            if len(columns) == 1:
                self.add_remove_column_button.setText("Удалить столбец")
                self.add_remove_column_button.disconnect()
                self.add_remove_column_button.clicked.connect(self.delete_column)
            else:
                self.add_remove_column_button.setText("Добавить столбец")
                self.add_remove_column_button.disconnect()
                self.add_remove_column_button.clicked.connect(self.add_column)

    def import_csv(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Открыть CSV файл", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if filePath:
            with open(filePath, 'r', newline='', encoding='utf-8') as file:
                self.data = []
                reader = csv.reader(file, delimiter=';')
                for row in reader:
                    # check if row was split considering ';' as delimiter
                    if len(row) == 1:
                        # try to split row considering ',' as delimiter
                        row = row[0].split(',')
                    self.data.append([cell.strip() for cell in row])
                    
                # Remove the header row
                self.data = self.data[1:]
                self.update_table()

    def import_xlsx(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Открыть XLSX файл", "", "XLSX Files (*.xlsx);;All Files (*)", options=options)
        if filePath:
            book = openpyxl.load_workbook(filePath, read_only=True)
            sheet = book.active
            self.data = [[cell for cell in row] for row in sheet.iter_rows(values_only=True)][1:]
            self.update_table()

    def update_table(self):
        self.table.clear()
        self.table.setRowCount(min(len(self.data), 10))  # limit to 10 rows
        self.table.setColumnCount(min(len(self.data[0]) if self.data else 0, 15))  # limit to 15 columns
        for row in range(len(self.data)):
            for col in range(len(self.data[row])):
                item = QTableWidgetItem(str(self.data[row][col]))
                item.setTextAlignment(Qt.AlignCenter)  # Set text alignment to center
                if row < 10 and col < 15:  # only add to the table if within limits
                    self.table.setItem(row, col, item)
        self.adjust_dialog_size()


    def add_column(self):
        for row_data in self.data:
            row_data.append('')
        self.update_table()
        self.adjust_dialog_size()

    def add_row(self):
        self.data.append(['' for _ in range(self.table.columnCount())])
        self.update_table()
        self.adjust_dialog_size()

    def delete_column(self):
        col_index = self.table.currentColumn()
        if col_index > -1:
            for row_data in self.data:
                del row_data[col_index]
            self.update_table()
        self.adjust_dialog_size()

    def delete_row(self):
        row_index = self.table.currentRow()
        if row_index > -1:
            del self.data[row_index]
            self.update_table()
        self.adjust_dialog_size()
    
    def get_data(self):
        return self.data

class ClickableTextItem(QGraphicsTextItem):
    def __init__(self, text, parent=None, list_widget1=None, list_widget2=None, filename = None):
        super().__init__(text, parent)
        self.setAcceptHoverEvents(True)
        self.filename = filename
        #print(f"list_widget2 in __init__: {list_widget2}")
        #self.list_widget2 = list_widget2
        #print(f"self.list_widget2 in __init__: {self.list_widget2}")
        
        # Set Flags
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        # Colors
        self.default_color = QColor(Qt.lightGray)  # Default color
        self.selected_color = QColor(Qt.darkGray)  # Color when selected

        # Initially set to default color
        self.current_color = self.default_color
        self.is_clicked = False  # Initially set to False
        
        # Reference to the list widget
        self.list_widget1 = list_widget1
        self.list_widget2 = list_widget2
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(11)

    def boundingRect(self):
        return super().boundingRect()  # Should return the correct bounding rect.

    @staticmethod
    def get_related_attributes(attribute_name, table_name, filename):
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        # Check if the attribute is a key in the given table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        is_key = any(col[1] == attribute_name and col[5] for col in columns)  # col[5] is pk column in PRAGMA output

        within_table_attributes = []
        within_database_attributes = []
        if is_key:
            # Within the same table: List all non-key attributes
            within_table_attributes.extend([col[1] for col in columns if not col[5]])  # col[5] is pk column in PRAGMA output

            # Within the database: List all key attributes of other tables that have direct relations to the selected table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                table = table[0]
                if table == table_name:  # skip the given table
                    continue
                
                #print(f"Examining table: {table}")  # Debugging line
                
                cursor.execute(f"PRAGMA foreign_key_list({table})")
                foreign_keys = cursor.fetchall()
                
                for fk in foreign_keys:
                    ref_table = fk[2]  # Reference table
                    ref_attribute = fk[3]  # Reference attribute (from column)
                    
                    #print(f"ref_table: {ref_table}, ref_attribute: {ref_attribute}")  # Debugging line
                    
                    if ref_table == table_name and ref_attribute == attribute_name:
                        #print(f"Match Found! Examining Columns of table: {table}")  # Debugging line
                        cursor.execute(f"PRAGMA table_info({table})")
                        table_columns = cursor.fetchall()
                        for col in table_columns:
                            is_pk = col[5]  # col[5] is pk column in PRAGMA output
                            col_name = col[1]  # col[1] is the name column in PRAGMA output
                            if is_pk:
                                #print(f"Adding: {col_name} to within_database_attributes")  # Debugging line
                                within_database_attributes.append(col_name)
        else:
            # If not a key, only list all attributes from the same table (both key and non-key)
            within_table_attributes.extend([col[1] for col in columns])

        connection.close()
        print(is_key, within_table_attributes, within_database_attributes)
        return is_key, within_table_attributes, within_database_attributes
    
    def populate_related_attributes(self):
        # Get the reference to the second list widget from the main app or another suitable place.
        #print("populate_related_attributes called")  # Debugging line
        second_list_widget = self.list_widget2
        
        #print(f"self.list_widget2 in populate_related_attributes: {self.list_widget2}")
        second_list_widget = self.list_widget2
        #print(second_list_widget)
        if second_list_widget is not None:
            #print("Second list widget found")  # Debugging line
            second_list_widget.clear()
            
            # Retrieve the parent_table object using the parentItem() method.
            parent_table = self.parentItem()
            
            if parent_table:
                #print("parent_table found")  # Debugging line
                attribute_name = self.toPlainText().split(" ")[0]  # Extract attribute name from displayed text
                table_name = parent_table.tableName  # Replace with the actual way to get table name from parent_table object
                
                # Get the related attributes by calling the function
                #print(f"Calling get_related_attributes with attribute_name={attribute_name}, table_name={table_name}")  # Debugging line
                try:
                    is_key, within_table_attributes, within_database_attributes = ClickableTextItem.get_related_attributes(attribute_name, table_name, self.filename)
                except Exception as e:
                    print(f"Error in calling get_related_attributes: {str(e)}")

                # If the attribute is a key, populate the widget with related attributes
                #print(f"is_key={is_key}, within_table_attributes={within_table_attributes}, within_database_attributes={within_database_attributes}")  # Debugging line
                if is_key:
                    second_list_widget.addItem("В выбранной таблице:")
                    for attribute in within_table_attributes:
                        second_list_widget.addItem(f"  {attribute}")

                    second_list_widget.addItem("В остальной Базе Данных:")
                    for attribute in within_database_attributes:
                        second_list_widget.addItem(f"  {attribute}")
                else:
                    # If not a key, just add the 'Within Table' category
                    second_list_widget.addItem("В выбранной таблице:")
                    for attribute in within_table_attributes:
                        second_list_widget.addItem(f"  {attribute}")


    def mousePressEvent(self, event):
        if self.is_clicked:
            self.is_clicked = False
            self.current_color = self.default_color
            self.remove_from_list()
            self.populate_related_attributes()
        else:
            self.is_clicked = True
            self.current_color = self.selected_color
            self.add_to_list()
            self.populate_related_attributes()

        self.update()  # trigger repaint
        super().mousePressEvent(event)

    def add_to_list(self):
        if self.list_widget1 is None:
            print("list_widget1 is None")
        else:
            print("list_widget1 is not None")
            #print(f"Adding {self.toPlainText()} to the list")
            self.list_widget1.addItem(self.toPlainText())

    def remove_from_list(self):
        if self.list_widget1 is None:
            print("list_widget is None")
        else:
            print("list_widget is not None")
            #print(f"Removing {self.toPlainText()} from the list")
            items = self.list_widget1.findItems(self.toPlainText(), Qt.MatchExactly)
            for item in items:
                row = self.list_widget1.row(item)
                self.list_widget1.takeItem(row)

    
    def paint(self, painter, option, widget=None):
        # Draw background rectangle
        painter.fillRect(self.boundingRect(), self.current_color)
        super().paint(painter, option, widget)


class RelationGraphicsItem(QGraphicsLineItem):
    def __init__(self, tableItem1, tableItem2, parent=None):
        super().__init__(parent)
        
        self.tableItem1 = tableItem1
        self.tableItem2 = tableItem2
                
        pen = QPen(QBrush(Qt.lightGray), 1)
        self.setPen(pen)

        line = QLineF(tableItem1.sceneBoundingRect().center(), tableItem2.sceneBoundingRect().center())
        self.setLine(line)
        
        tableItem1.relations.append(self)
        tableItem2.relations.append(self)

        self.setZValue(5)  # Lines at the bottom
        self.relations = []
    
class TableGraphicsItem(QGraphicsRectItem):
    def __init__(self, tableName, columns, parent=None, list_widget1=None, list_widget2=None, filename = None):
        super().__init__(parent)
        
        self.tableName = tableName
        self.columns = columns
        self.relations = []
        self.setZValue(9) # Tables just below the titles

        self.setBrush(QBrush(Qt.gray))  # Set to gray or your preferred color
        self.setRect(QRectF(0, 0, 150, 30 + 20 * len(columns)))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        title_bg = QGraphicsRectItem(0, 0, 150, 30, self)
        title_bg.setBrush(QBrush(Qt.lightGray))
        title_bg.setZValue(10)  # Table titles on top
        
        title = QGraphicsTextItem(tableName, self)
        title.setPos(10, 5)
        title.setZValue(10)  # Table titles on top
        
        for i, (colName, colType) in enumerate(columns):
            textItem = ClickableTextItem(f"{colName} ({colType})", self, list_widget1=list_widget1, list_widget2=list_widget2, filename = filename)
            textItem.setPos(10, 35 + i * 20)
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:  # Notice the change here
            self.update_relations()

        return super().itemChange(change, value)

    def update_relations(self):
        for relation in self.relations:
            rect1 = self.sceneBoundingRect()
            rect2 = relation.tableItem2.sceneBoundingRect() if relation.tableItem1 == self else relation.tableItem1.sceneBoundingRect()

            center1 = rect1.center()
            center2 = rect2.center()

            line = QLineF(center1, center2)

            p1_intersect = self.calculate_intersection(rect1, line)
            p2_intersect = self.calculate_intersection(rect2, line)

            if p1_intersect and p2_intersect:
                new_line = QLineF(p1_intersect, p2_intersect)
                relation.setLine(new_line)
    
    def calculate_intersection(self, rect, line):
        # Generate lines for each edge of the rectangle
        lines = [
            QLineF(rect.topLeft(), rect.topRight()),
            QLineF(rect.topRight(), rect.bottomRight()),
            QLineF(rect.bottomRight(), rect.bottomLeft()),
            QLineF(rect.bottomLeft(), rect.topLeft()),
        ]

        for rect_line in lines:
            intersection_point = QPointF()
            # Find the intersection point between the rectangle edge and the line
            result = line.intersect(rect_line, intersection_point)
            if result == QLineF.BoundedIntersection:
                return intersection_point

        return None

class CalculateAlternativesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Main Layout
        main_layout = QHBoxLayout(self)
        
        # Left Widget for Graphics View
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        left_layout.addWidget(self.view)
        
        # Right Widget for ListWidgets
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # First ListWidget and its GroupBox
        self.table_list1 = QListWidget()
        self.table_list1.setStyleSheet("background-color: #F0F0F0;")
        list_group_box1 = QGroupBox("Выбранные аттрибуты:")
        list_group_box1.setLayout(QVBoxLayout())
        list_group_box1.layout().addWidget(self.table_list1)
        right_layout.addWidget(list_group_box1)
        
        # Second ListWidget and its GroupBox
        self.table_list2 = QListWidget()
        self.table_list2.setStyleSheet("background-color: #F0F0F0;")
        list_group_box2 = QGroupBox("Рекомендуемые аттрибуты:")
        list_group_box2.setLayout(QVBoxLayout())
        list_group_box2.layout().addWidget(self.table_list2)
        right_layout.addWidget(list_group_box2)

        #Button for continuing
        continueButton = QPushButton("Далее")
        right_layout.addWidget(continueButton)
        
        # Add Left and Right Widgets to Main Layout
        main_layout.addWidget(left_widget, 2)  # GraphicsView will take 2 parts of the available space
        main_layout.addWidget(right_widget, 1)  # ListWidgets will take 1 part of the available space
        
        # Window Setup
        self.setGeometry(100, 100, 1300, 600)  # Adjusted the window width
        self.setWindowTitle('Определение аттрибутов из БД')
        
        self.center_on_screen()
        self.show()
        
        # Load Tables
        self.openFileNameDialog()
        
    def showEvent(self, event):
        self.center_on_screen()
        super().showEvent(event)

    def center_on_screen(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Открыть файл БД SQLite", "", "SQLite Databases (*.db);;All Files (*)", options=options)
        if fileName:
            self.loadTables(fileName)
    
    def loadTables(self, dbFile):
        conn = sqlite3.connect(dbFile)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        tableItems = {}
        x = 10
        y = 10
        max_height = 0
        for table in tables:
            tableName = table[0]
            cursor.execute(f"PRAGMA table_info({tableName});")
            columns = [(col[1], col[2]) for col in cursor.fetchall()]
            tableItem = TableGraphicsItem(tableName, columns, list_widget1=self.table_list1, list_widget2=self.table_list2, filename=dbFile)
            tableItem.setPos(x, y)
            self.scene.addItem(tableItem)
            tableItems[tableName] = tableItem
            
            rect = tableItem.rect()
            max_height = max(max_height, rect.height())
            y += max_height + 20
            
            if y > self.view.height() - max_height - 20:
                y = 10
                x += rect.width() + 50
        
        for tableName, tableItem in tableItems.items():
            cursor.execute(f"PRAGMA foreign_key_list({tableName});")
            for relation in cursor.fetchall():
                referencedTable = relation[2]
                if referencedTable in tableItems:
                    lineItem = RelationGraphicsItem(tableItem, tableItems[referencedTable])
                    
                    self.scene.addItem(lineItem)
                    tableItem.relations = getattr(tableItem, 'relations', [])
                    tableItem.relations.append(lineItem)
        conn.close()
        
    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.setResizeAnchor(QGraphicsView.NoAnchor)
        oldPos = self.view.mapToScene(event.pos())
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.view.scale(zoomFactor, zoomFactor)
        newPos = self.view.mapToScene(event.pos())
        delta = newPos - oldPos
        self.view.translate(delta.x(), delta.y())

class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.initUI()
        self.dbwindow = None
        self.alternatives_data = None
        self.assessment_window = None

    def initUI(self):
        self.setWindowTitle('Многокритериальная оценка данных')
        layout = QVBoxLayout(self.central_widget)

        calculate_button = QPushButton("Определить альтернативы")
        calculate_button.clicked.connect(self.calculate_alternatives)

        input_button = QPushButton("Ввести альтернативы")
        input_button.clicked.connect(self.input_alternatives)

        self.assessment_button = QPushButton("Определить параметры оценки")
        self.assessment_button.setEnabled(False)
        self.assessment_button.clicked.connect(self.assessment)

        layout.addWidget(calculate_button)
        layout.addWidget(input_button)
        layout.addWidget(self.assessment_button)

        self.center_on_screen()
        self.show()

    def showEvent(self, event):
        self.center_on_screen()
        super().showEvent(event)

    def center_on_screen(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def calculate_alternatives(self):
        self.dbwindow = CalculateAlternativesWindow()
        self.dbwindow.show()
        if self.dbwindow.close:
            self.assessment_button.setEnabled(True)

    def input_alternatives(self):
        self.hide()
        window = InputAlternativesWindow()
        if window.exec_() == QDialog.Accepted:  # QDialog.Accepted is returned when 'Save' is pressed
            self.alternatives_data = window.get_data()  # Store table data as state
            self.assessment_button.setEnabled(True)
        self.center_on_screen()
        self.show()

    def assessment(self):
        self.hide()
        self.assessment_window = AssessmentWindow(self.alternatives_data)
        self.assessment_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
