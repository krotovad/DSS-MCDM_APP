import csv
import sys
import openpyxl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDialog, 
                             QFileDialog, QAction, QLabel, QSizePolicy, QStackedWidget, 
                             QListWidget, QTextEdit, QAbstractItemView, QListWidgetItem, QGroupBox,
                             QFrame, QHBoxLayout, QCheckBox, QGridLayout)

class AssessmentWindow(QWidget):
    def __init__(self, data):
        super(AssessmentWindow, self).__init__()
        self.data = data
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 400)
        self.setWindowTitle('Assessment Window')

        grid_layout = QGridLayout(self)

        # 1. Section for List of Multicriterial Assessment Methods
        self.method_group = QGroupBox("Multicriterial Assessment Methods")
        self.method_list = QListWidget(self.method_group)

        categories_methods = {
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
        font.setPointSize(14)
        self.info_widget.setFont(font)
        self.info_widget.setPlaceholderText("This widget displays information about the selected method.")
        grid_layout.addWidget(self.info_widget, 0, 1)

        # 3. Additional Section for Additional Inputs
        self.additional_input = QTextEdit(self)
        self.additional_input.setText("No additional inputs needed")
        grid_layout.addWidget(self.additional_input, 1, 0, 1, 2)  # Spanning the widget across both columns

    def display_info(self):
        info = ""
        additional_section_visible = False
        additional_inputs_needed = False

        method_descriptions = {
            'TOPSIS': """
            Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS)
            -----------------------------------------
            - Approach: Compares each alternative against a theoretically ideal solution.
            - Inputs: Requires an evaluation matrix consisting of m alternatives and n criteria.
            - Additional Inputs: Weights of criteria, and the impact (benefit/cost) of the criteria.
            - Output: Ranking of alternatives.
            - Ideal for: Problems where the best alternative needs to be chosen out of a given set.
            """,
            
            'WSR': """
            Weighted Sum Model (WSM) or Weighted Linear Combination
            ----------------------------------------------------
            - Approach: Assigns weights based on the importance of each criterion.
            - Inputs: Scores of each alternative on each criterion.
            - Additional Inputs: Weights of criteria.
            - Output: Single overall score for each alternative.
            - Ideal for: Situations where trade-offs between criteria are possible.
            """,
            
            'ELECTRE': """
            Elimination Et Choix Traduisant la Realité (ELECTRE)
            ---------------------------------------------------
            - Approach: Eliminates alternatives that do not meet certain criteria.
            - Inputs: Performance table consisting of the performance of each alternative on each criterion.
            - Additional Inputs: Weights of criteria, concordance, and discordance thresholds.
            - Output: Partial pre-order of alternatives.
            - Ideal for: Problems with conflicting criteria where a set of all potential good solutions is needed.
            """,
            
            'VIKOR': """
            VlseKriterijumska Optimizacija I Kompromisno Resenje (VIKOR)
            ----------------------------------------------------------
            - Approach: Introduces the multi-criteria ranking index based on the particular measure of 'closeness' to the 'ideal' solution.
            - Inputs: Matrix of alternative assessments according to all criteria.
            - Additional Inputs: Weights of criteria.
            - Output: Compromise solution and ranking list.
            - Ideal for: Societal decision-making problems, especially for resolving the water resources allocation problem.
            """
        }

        for index in range(self.method_list.count()):
            item = self.method_list.item(index)
            widget = self.method_list.itemWidget(item)
            if widget and isinstance(widget, QCheckBox) and widget.isChecked():
                method = widget.text()
                if method in method_descriptions:
                    info += method_descriptions[method] + "\n\n"
                if method in ['TOPSIS', 'WSR', 'ELECTRE', 'VIKOR']:
                    additional_inputs_needed = True

        self.info_widget.setText(info)
        if additional_inputs_needed:
            self.additional_input.setText("Additional inputs are needed for the selected method(s).")
        else:
            self.additional_input.setText("No additional inputs needed")


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
        self.table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.table.itemSelectionChanged.connect(self.handle_item_selection)
        
        # Place the table and button_layout in a horizontal layout
        h_layout = QVBoxLayout()
        h_layout.addLayout(self.button_layout)  # Add button_layout (import and add/remove buttons) to the horizontal layout
        h_layout.addWidget(self.table)  # Add table to the horizontal layout
        
        self.main_layout.addLayout(h_layout)  # Add horizontal layout to the main layout
        self.main_layout.addLayout(self.save_cancel_layout)  # Add save_cancel_layout below the horizontal layout
        self.main_layout.addStretch(1)
        self.adjustSize()
        #self.adjust_dialog_size()

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
        self.button_layout = QHBoxLayout()
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
        self.save_cancel_layout = QHBoxLayout()  # Changed to QHBoxLayout to put buttons side by side
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
        self.table.setRowCount(len(self.data))  # limit to 10 rows
        self.table.setColumnCount(len(self.data[0]))  # limit to 15 columns
        for row in range(len(self.data)):
            for col in range(len(self.data[row])):
                item = QTableWidgetItem(str(self.data[row][col]))
                item.setTextAlignment(Qt.AlignCenter)  # Set text alignment to center
                if row < 10 and col < 15:  # only add to the table if within limits
                    self.table.setItem(row, col, item)
        #self.adjust_dialog_size()
        self.adjustSize()


    def add_column(self):
        for row_data in self.data:
            row_data.append('')
        self.update_table()
        #self.adjust_dialog_size()

    def add_row(self):
        self.data.append(['' for _ in range(self.table.columnCount())])
        self.update_table()
        #self.adjust_dialog_size()

    def delete_column(self):
        col_index = self.table.currentColumn()
        if col_index > -1:
            for row_data in self.data:
                del row_data[col_index]
            self.update_table()
        #self.adjust_dialog_size()

    def delete_row(self):
        row_index = self.table.currentRow()
        if row_index > -1:
            del self.data[row_index]
            self.update_table()
        #self.adjust_dialog_size()
    
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
        layout = QHBoxLayout(self.central_widget)

        calculate_button = QPushButton("Calculate Alternatives")
        calculate_button.clicked.connect(self.calculate_alternatives)

        input_button = QPushButton("Input Alternatives")
        input_button.clicked.connect(self.input_alternatives)

        self.assessment_button = QPushButton("Multicriterial Assessment")
        self.assessment_button.setEnabled(False)
        self.assessment_button.clicked.connect(self.assessment)

        calculate_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        input_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.assessment_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
