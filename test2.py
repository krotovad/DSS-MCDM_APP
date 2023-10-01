import csv
import sys
import openpyxl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDialog, QTabWidget, 
                             QFileDialog, QAction, QLabel, QSizePolicy, QStackedWidget, 
                             QListWidget, QTextEdit, QAbstractItemView, QListWidgetItem, QGroupBox,
                             QFrame, QHBoxLayout, QCheckBox, QGridLayout, QLineEdit, QFormLayout, QHeaderView)

method_descriptions = {
    'MINSUM': {
        'description': (
        'Minimum Sum (MINSUM)\n'
        '-------------------\n'
        '- Approach: Aggregates the evaluations of alternatives based on the sum of their scores, giving preference to the alternatives with the lowest total score.\n'
        '- Inputs: Requires an evaluation matrix consisting of m alternatives and n criteria.\n'
        '- Output: A single preferred alternative.\n'
        '- Ideal for: Problems where the decision-maker prefers to minimize the aggregate evaluations, suitable for cost minimization problems.'
        ),
        'args': [
            
        ]
    },
    'MINMAX': {
        'description': (
        'Minimum Maximum (MINMAX)\n'
        '-----------------------\n'
        '- Approach: Chooses the alternative that has the least maximum value, minimizing the worst-case outcome.\n'
        '- Inputs: Requires an evaluation matrix consisting of m alternatives and n criteria.\n'
        '- Output: A single preferred alternative.\n'
        '- Ideal for: Decision-making situations where risk avoidance is crucial, and the decision-maker wants to avoid the worst possible outcome.'
        ),
        'args': [
            
        ]
    },
    'MAXMIN': {
        'description': (
        'Maximum Minimum (MAXMIN)\n'
        '-----------------------\n'
        '- Approach: Selects the alternative that has the greatest minimum value, maximizing the worst-case outcome.\n'
        '- Inputs: Requires an evaluation matrix consisting of m alternatives and n criteria.\n'
        '- Output: A single preferred alternative.\n'
        '- Ideal for: Scenarios focusing on benefiting the most from the least favorable conditions, suitable for robustness analysis.'
        ),
        'args': [
            
        ]
    },'TOPSIS': {
        'description': (
            'Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS)\n'
            '-----------------------------------------\n'
            '- Approach: Compares each alternative against a theoretically ideal solution.\n'
            '- Inputs: Requires an evaluation matrix consisting of m alternatives and n criteria.\n'
            '- Output: Ranking of alternatives.\n'
            '- Ideal for: Problems where the best alternative needs to be chosen out of a given set.'
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
            'Weighted Sum Model (WSM) or Weighted Linear Combination\n'
            '----------------------------------------------------\n'
            '- Approach: Assigns weights based on the importance of each criterion.\n'
            '- Inputs: Scores of each alternative on each criterion.\n'
            '- Output: Single overall score for each alternative.\n'
            '- Ideal for: Situations where trade-offs between criteria are possible.'
        ),
        'args': [
            {
                'name': 'Weights',
                'type': 'multiple',
                'applies_to': 'each_criteria'
            },
            # Add other arguments if needed
        ]
    },
    'ELECTRE': {
        'description': (
            'Elimination Et Choix Traduisant la Realité (ELECTRE)\n'
            '---------------------------------------------------\n'
            '- Approach: Eliminates alternatives that do not meet certain criteria.\n'
            '- Inputs: Performance table consisting of the performance of each alternative on each criterion.\n'
            '- Output: Partial pre-order of alternatives.\n'
            '- Ideal for: Problems with conflicting criteria where a set of all potential good solutions is needed.'
        ),
        'args': [
            {
                'name': 'Concordance Threshold',
                'type': 'singular',
                'applies_to': 'all'
            },
            {
                'name': 'Discordance Threshold',
                'type': 'singular',
                'applies_to': 'all'
            },
            # Add other arguments if needed
        ]
    },
    'VIKOR': {
        'description': (
            "VlseKriterijumska Optimizacija I Kompromisno Resenje (VIKOR)\n"
            "----------------------------------------------------------\n"
            "- Approach: Introduces the multi-criteria ranking index based on the particular measure of 'closeness' to the 'ideal' solution.\n"
            "- Inputs: Matrix of alternative assessments according to all criteria.\n"
            "- Output: Compromise solution and ranking list.\n"
            "- Ideal for: Societal decision-making problems, especially for resolving the water resources allocation problem."
        ),
        'args': [
            {
                'name': 'Weights',
                'type': 'multiple',
                'applies_to': 'each_criteria'
            },
            # Add other arguments if needed
        ]
    }
}

class ResultsWindow(QWidget):
    def __init__(self, data, methods, inputs):
        super(ResultsWindow, self).__init__()

        # Initialize class variables with the provided arguments
        self.data = data
        self.methods = methods
        self.inputs = inputs

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        data_display_layout = QHBoxLayout()

        # 1. Display Data
        data_label = QLabel('Data:')
        data_display_layout.addWidget(data_label)

        self.data_table = QTableWidget()
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setDataTable()
        data_display_layout.addWidget(self.data_table, 1)

        paretoButton = QPushButton("Sort out Non-Optimal alternatives")
        paretoButton.clicked.connect(self.paretoCleanUp)
        data_display_layout.addWidget(paretoButton)
        
        #2. results section
        results_layout = QHBoxLayout()
        tabs = QTabWidget()
        tabs_layout = QHBoxLayout()
        for method in self.methods:
            print(method)
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)  # Create a layout for the tab
            tabs.addTab(tab, method)  # Add the tab to the QTabWidget with the name from the list
            
        tabs_layout.addWidget(tabs)
        
        results_layout.addLayout(tabs_layout, 1)

        main_layout.addLayout(data_display_layout, 1)
        main_layout.addLayout(results_layout, 1)
        self.setLayout(main_layout)

    def pareto_dominance(data):
        pareto_front = []  # List to store the pareto front alternatives
        for i, alt1 in enumerate(data):
            dominated = False  # Initially, assume alt1 is not dominated by any alternative
            for j, alt2 in enumerate(data):
                if i != j:  # Ensure we are not comparing the alternative with itself
                    if all(a >= b for a, b in zip(alt1[1:], alt2[1:])) and any(a > b for a, b in zip(alt1[1:], alt2[1:])):
                        # alt2 dominates alt1
                        dominated = True
                        break  # No need to compare with other alternatives
            if not dominated:
                pareto_front.append(alt1)  # alt1 is not dominated by any alternative, so it is part of the Pareto front
        return pareto_front
    
    def minsum(self):
        minsum_list = []
        for row in self.data:
            # Assuming the first element in each row is the alternative name
            # So, we skip it during the sum operation
            sum_value = sum(row[1:]) 
            minsum_list.append([sum_value] + [row[0]])  # [sum_value, alternative_name]
            
        # Sort the list in ascending order of sum_value
        minsum_list.sort(key=lambda x: x[0])
        return minsum_list

    def minmax(self):
        minmax_list = []
        for row in self.data:
            minmax_value = max(row[1:])  # Skip the first element as it's the alternative name
            minmax_list.append([minmax_value] + [row[0]])  # [minmax_value, alternative_name]

        # Sort the list in ascending order of minmax_value, so as to minimize the maximum value
        minmax_list.sort(key=lambda x: x[0])
        return minmax_list


    def maxmin(self):
        maxmin_list = []
        for row in self.data:
            maxmin_value = min(row[1:])  # Skip the first element as it's the alternative name
            maxmin_list.append([maxmin_value] + [row[0]])  # [maxmin_value, alternative_name]

        # Sort the list in descending order of maxmin_value, so as to maximize the minimum value
        maxmin_list.sort(key=lambda x: x[0], reverse=True)
        return maxmin_list

    def topsis(self):
        # Ensure the weights are in float
        weights = [float(weight) for weight in self.inputs]
        
        # Get the normalized decision matrix
        normalized_decision_matrix = []
        for col in range(1, len(self.data[0])):
            column = [row[col] for row in self.data]
            norm = (sum(x**2 for x in column)) ** 0.5
            normalized_decision_matrix.append([x / norm for x in column])
        
        # Get the weighted normalized decision matrix
        weighted_normalized_decision_matrix = [[val * weights[i] for val in col] for i, col in enumerate(normalized_decision_matrix)]
        
        # Determine the ideal and negative-ideal solutions
        ideal_solution = [max(col) for col in weighted_normalized_decision_matrix]
        negative_ideal_solution = [min(col) for col in weighted_normalized_decision_matrix]
        
        # Calculate the separation measures
        separation_measures = []
        for row in range(len(self.data)):
            s_positive = sum((weighted_normalized_decision_matrix[col][row] - ideal_solution[col]) ** 2 for col in range(len(ideal_solution))) ** 0.5
            s_negative = sum((weighted_normalized_decision_matrix[col][row] - negative_ideal_solution[col]) ** 2 for col in range(len(negative_ideal_solution))) ** 0.5
            separation_measures.append((s_negative / (s_positive + s_negative), self.data[row][0]))  # (Closeness coefficient, alternative)
        
        # Rank the alternatives
        ranked_alternatives = sorted(separation_measures, key=lambda x: x[0], reverse=True)
        return [[alternative] + values for values, alternative in ranked_alternatives]

    def electre(data):
        # This is a placeholder. ELECTRE usually involves a more complex procedure with concordance and discordance indices, thresholds, etc.
        return [sum(alternative[1:]) for alternative in data]  # placeholder, please replace with actual implementation

    def vikor(data):
        # This is a placeholder. VIKOR usually involves more complex computations including weighting, utility, and regret measures.
        return [sum(alternative[1:]) for alternative in data]  # placeholder, please replace with actual implementation

    def setDataTable(self):
        row_count = len(self.data)
        col_count = len(self.data[0])
        self.data_table.setRowCount(row_count)
        self.data_table.setColumnCount(col_count)

        for row_index, row_data in enumerate(self.data):
            for col_index, cell_data in enumerate(row_data):
                self.data_table.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))

class AssessmentWindow(QWidget):
    def __init__(self, data):
        super(AssessmentWindow, self).__init__()
        self.data = data
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 400)
        self.setWindowTitle('Assessment Window')
        self.selected_methods = []
        self.additional_inputs = {}

        grid_layout = QGridLayout(self)

        # 1. Section for List of Multicriterial Assessment Methods
        self.method_group = QGroupBox("Multicriterial Assessment Methods")
        self.method_list = QListWidget(self.method_group)

        categories_methods = {
            'Primitives': ['MINSUM', 'MINMAX', 'MAXMIN'],
            'Decision Making Methods': ['TOPSIS', 'WSR'],
            'Outranking Methods': ['ELECTRE'],
            'Compromise Ranking Methods': ['VIKOR']
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
        self.info_widget.setPlaceholderText("This widget displays information about the selected method.")
        grid_layout.addWidget(self.info_widget, 0, 1)

        self.resultsButton = QPushButton("Save and Continue")
        self.resultsButton.clicked.connect(lambda: self.showResults(self.data, self.selected_methods, self.read_input_fields()))
        grid_layout.addWidget(self.resultsButton, 0, 2)

        # 3. Additional Section for Additional Inputs
        self.additional_inputs_group = QGroupBox("Additional Inputs")
        self.form_layout = QFormLayout()
        self.input_instruction_label = QLabel()
        self.form_layout.addRow(self.input_instruction_label)
        self.additional_inputs_group.setLayout(self.form_layout)
        grid_layout.addWidget(self.additional_inputs_group, 1, 0, 1, 2)
        grid_layout.setRowStretch(0, 1)  # Stretch the first row so that it takes up the available space
        grid_layout.setRowStretch(1, 0)  # Do not stretch the second row
        #self.additional_inputs_group.hide()  # Hide by default

        self.method_list.itemSelectionChanged.connect(self.display_info)
        #self.additional_inputs = dict()
        
    def showResults(self, data, methods, inputs):
        print(data, methods, inputs)
        self.hide()        
        self.resultsWindow = ResultsWindow(data, methods, inputs)
        self.resultsWindow.show()
        self.show()        
    
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
            print(f"Additional Inputs Group is Visible: {self.additional_inputs_group.isVisible()}")
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

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_pressed)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)
        self.save_pressed_flag = False

    def save_pressed(self):
        print("Save pressed in Calculate Alternatives window")
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
        self.import_csv_button = QPushButton("Import from CSV", self)
        self.import_xlsx_button = QPushButton("Import from XLSX", self)
        self.add_remove_column_button = QPushButton("Add Column", self)
        self.add_remove_row_button = QPushButton("Add Row", self)

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
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)
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
        self.add_remove_row_button.setText("Add Row")
        self.add_remove_row_button.disconnect()
        self.add_remove_row_button.clicked.connect(self.add_row)

        self.add_remove_column_button.setText("Add Column")
        self.add_remove_column_button.disconnect()
        self.add_remove_column_button.clicked.connect(self.add_column)
    
    def handle_item_selection(self):
        selected_indices = self.table.selectedIndexes()
        if selected_indices:
            rows = set(index.row() for index in selected_indices)
            columns = set(index.column() for index in selected_indices)
            if len(rows) == 1:
                self.add_remove_row_button.setText("Delete Row")
                self.add_remove_row_button.disconnect()
                self.add_remove_row_button.clicked.connect(self.delete_row)
            else:
                self.add_remove_row_button.setText("Add Row")
                self.add_remove_row_button.disconnect()
                self.add_remove_row_button.clicked.connect(self.add_row)

            if len(columns) == 1:
                self.add_remove_column_button.setText("Delete Column")
                self.add_remove_column_button.disconnect()
                self.add_remove_column_button.clicked.connect(self.delete_column)
            else:
                self.add_remove_column_button.setText("Add Column")
                self.add_remove_column_button.disconnect()
                self.add_remove_column_button.clicked.connect(self.add_column)

    def import_csv(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
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
        filePath, _ = QFileDialog.getOpenFileName(self, "Open XLSX File", "", "XLSX Files (*.xlsx);;All Files (*)", options=options)
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

class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.initUI()
        self.alternatives_data = None
        self.assessment_window = None

    def initUI(self):
        self.setWindowTitle('Main Layout')
        layout = QVBoxLayout(self.central_widget)

        calculate_button = QPushButton("Calculate Alternatives")
        calculate_button.clicked.connect(self.calculate_alternatives)

        input_button = QPushButton("Input Alternatives")
        input_button.clicked.connect(self.input_alternatives)

        self.assessment_button = QPushButton("Multicriterial Assessment")
        self.assessment_button.setEnabled(False)
        self.assessment_button.clicked.connect(self.assessment)

        layout.addWidget(calculate_button)
        layout.addWidget(input_button)
        layout.addWidget(self.assessment_button)

        self.show()

    def calculate_alternatives(self):
        print("Calculating Alternatives...")
        window = CalculateAlternativesWindow()
        window.exec_()
        if window.save_pressed_flag:
            self.assessment_button.setEnabled(True)

    def input_alternatives(self):
        print("Inputting Alternatives...")
        self.hide()
        window = InputAlternativesWindow()
        if window.exec_() == QDialog.Accepted:  # QDialog.Accepted is returned when 'Save' is pressed
            self.alternatives_data = window.get_data()  # Store table data as state
            self.assessment_button.setEnabled(True)
        self.show()

    def assessment(self):
        print("Performing Multicriterial Assessment...")
        self.hide()
        self.assessment_window = AssessmentWindow(self.alternatives_data)
        self.assessment_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
