import csv
import sys
import openpyxl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDialog, 
                             QFileDialog, QAction, QLabel, QSizePolicy, QStackedWidget, 
                             QListWidget, QTextEdit, QAbstractItemView, QListWidgetItem, QGroupBox,
                             QFrame, QHBoxLayout, QCheckBox, QGridLayout, QFormLayout, QLineEdit)

class AssessmentWindow(QWidget):
    def __init__(self, data):
        super(AssessmentWindow, self).__init__()
        self.data = data
        self.num_args = len(data[0]) - 1  # Assuming data[0] is a row, and the first element is a function
        self.num_funcs = len(data)  # Assuming each row is a different function
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
        self.additional_inputs_group = QGroupBox("Additional Inputs")
        self.form_layout = QFormLayout()
        self.input_instruction_label = QLabel()
        self.form_layout.addRow(self.input_instruction_label)
        self.additional_inputs_group.setLayout(self.form_layout)
        grid_layout.addWidget(self.additional_inputs_group, 1, 0, 1, 2)
        self.additional_inputs_group.hide()  # Hide by default

          
    def display_info(self):
        info = ""
        additional_inputs = set()

        method_additional_inputs = {
            'TOPSIS': ["Weights of criteria"],
            'WSR': ["Weights of criteria"],
            'ELECTRE': ["Weights of criteria", "Concordance threshold", "Discordance threshold"],
            'VIKOR': ["Weights of criteria"]
        }

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
        
        # Clearing the existing form layout
        while self.form_layout.count() > 1:  # keep the instruction label
            child = self.form_layout.takeAt(1)  # remove from index 1
            if child.widget():
                child.widget().deleteLater()

        required_inputs = {}
        
        for index in range(self.method_list.count()):
            item = self.method_list.item(index)
            widget = self.method_list.itemWidget(item)
            if widget and isinstance(widget, QCheckBox) and widget.isChecked():
                method = widget.text()
                if method in ['TOPSIS', 'WSR']:
                    input_needed = "Weights of criteria"
                elif method == 'ELECTRE':
                    input_needed = "Weights of criteria, concordance, and discordance thresholds"
                elif method == 'VIKOR':
                    input_needed = "Weights of criteria"
                else:
                    continue

                if input_needed in required_inputs:
                    required_inputs[input_needed].append(method)
                else:
                    required_inputs[input_needed] = [method]
        
        if required_inputs:
            instructions = []
            for input_needed, methods in required_inputs.items():
                instructions.append(f"Input {input_needed} for method(s) {', '.join(methods)}:")
                for i in range(self.num_args):
                    self.form_layout.addRow(QLabel(f"{input_needed} Arg {i + 1}"), QLineEdit())
                for i in range(self.num_funcs):
                    self.form_layout.addRow(QLabel(f"{input_needed} Func {i + 1}"), QLineEdit())
            self.input_instruction_label.setText("\n".join(instructions))
            self.additional_inputs_group.show()
        else:
            self.input_instruction_label.clear()
            self.additional_inputs_group.hide()

if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    
    # If you have a specific `data` variable to pass, replace `None` with your data.
    window = AssessmentWindow(None)  
    
    window.show()
    sys.exit(app.exec_())
