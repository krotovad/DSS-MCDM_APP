"""
UI Components module for MCDA application
Contains all PyQt-based GUI components
"""

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Modern styling
STYLE_SHEET = """
QWidget {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background-color: #f0f0f0;
}

QMenuBar {
    background-color: #2c3e50;
    color: white;
    padding: 4px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background: #34495e;
}

QMenuBar::item:pressed {
    background: #3d566e;
}

QMenu {
    background-color: #ecf0f1;
    border: 1px solid #bdc3c7;
    color: #2c3e50;
}

QMenu::item {
    padding: 6px 15px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #bdc3c7;
    border-radius: 8px;
    margin-top: 1ex;
    padding-top: 10px;
    background-color: #ffffff;
}

QLabel {
    color: #2c3e50;
}

QLineEdit {
    border: 2px solid #bdc3c7;
    border-radius: 4px;
    padding: 5px;
    background-color: #ffffff;
    color: #2c3e50;
}

QLineEdit:focus {
    border-color: #3498db;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #bdc3c7;
}

QCheckBox {
    spacing: 8px;
    color: #2c3e50;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #bdc3c7;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    border: 2px solid #3498db;
    border-radius: 3px;
    background-color: #3498db;
    image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAFNJREFUeNpiYMAAXDx8/zEwMPzHweoAxAEhLiYmJvzGsiADGCA0VykmJib8xrIgA1gQGsOCrBEGJpLMxcXF/YeBAQECDAARSwqZkQmVVgAAAABJRU5ErkJggg==);
}

QTableWidget {
    border: 2px solid #bdc3c7;
    gridline-color: #ecf0f1;
    background-color: #ffffff;
    alternate-background-color: #f9f9f9;
}

QHeaderView::section {
    background-color: #3498db;
    color: white;
    padding: 6px;
    border: 1px solid #2980b9;
    font-weight: bold;
}

QTabWidget::pane {
    border: 2px solid #bdc3c7;
    border-radius: 8px;
    background: #ffffff;
}

QTabBar::tab {
    background: #bdc3c7;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #3498db;
    color: white;
}

QScrollBar:vertical {
    background: #ecf0f1;
    width: 15px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #bdc3c7;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #95a5a6;
}

QMessageBox {
    background-color: #ecf0f1;
}

QProgressBar {
    border: 2px solid #bdc3c7;
    border-radius: 5px;
    text-align: center;
    color: #2c3e50;
}

QProgressBar::chunk {
    background-color: #3498db;
    border-radius: 4px;
}
"""


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """Initialize the main UI elements"""
        self.setWindowTitle('MCDA Analysis Tool')
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply modern style sheet
        self.setStyleSheet(STYLE_SHEET)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        load_action = QAction('Load Data', self)
        load_action.triggered.connect(self.load_data)
        file_menu.addAction(load_action)
        
        save_action = QAction('Save Results', self)
        save_action.triggered.connect(self.save_results)
        file_menu.addAction(save_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Main content area
        self.setup_main_content(main_layout)
        
    def setup_main_content(self, layout):
        """Setup the main content area"""
        # Input section
        input_group = QGroupBox("Input Parameters")
        input_layout = QGridLayout(input_group)
        
        # Number of alternatives
        input_layout.addWidget(QLabel("Number of Alternatives:"), 0, 0)
        self.num_alternatives_input = QLineEdit()
        self.num_alternatives_input.setText("3")
        self.num_alternatives_input.setPlaceholderText("Enter number of alternatives...")
        input_layout.addWidget(self.num_alternatives_input, 0, 1)
        
        # Number of criteria
        input_layout.addWidget(QLabel("Number of Criteria:"), 1, 0)
        self.num_criteria_input = QLineEdit()
        self.num_criteria_input.setText("4")
        self.num_criteria_input.setPlaceholderText("Enter number of criteria...")
        input_layout.addWidget(self.num_criteria_input, 1, 1)
        
        # Weights input
        input_layout.addWidget(QLabel("Weights (comma-separated):"), 2, 0)
        self.weights_input = QLineEdit()
        self.weights_input.setText("0.25,0.25,0.25,0.25")
        self.weights_input.setPlaceholderText("Enter weights separated by commas...")
        input_layout.addWidget(self.weights_input, 2, 1)
        
        # Methods selection
        methods_group = QGroupBox("MCDA Methods")
        methods_layout = QGridLayout(methods_group)  # Changed to QGridLayout for better organization
        
        # Create checkboxes for methods in a grid layout
        self.method_checkboxes = {}
        methods = [
            'MINSUM', 'MINMAX', 'MAXMIN', 'DIP', 'TOPSIS',
            'WSR', 'ELECTRE', 'VIKOR', 'ОРП', 'AHP', 'CHP',
            'PROMETHEE', 'GRA', 'F-AHP', 'DEMATEL'
        ]
        
        # Arrange method checkboxes in a 4x4 grid
        for idx, method in enumerate(methods):
            row = idx // 4
            col = idx % 4
            checkbox = QCheckBox(method)
            checkbox.setChecked(True)
            self.method_checkboxes[method] = checkbox
            methods_layout.addWidget(checkbox, row, col)
            
        # Data table
        data_group = QGroupBox("Data Table")
        data_layout = QVBoxLayout(data_group)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(4)
        self.data_table.setHorizontalHeaderLabels([f"Criterion {i+1}" for i in range(4)])
        data_layout.addWidget(self.data_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Table")
        generate_btn.clicked.connect(self.generate_table)
        button_layout.addWidget(generate_btn)
        
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.analyze)
        button_layout.addWidget(analyze_btn)
        
        # Add widgets to main layout
        layout.addWidget(input_group)
        layout.addWidget(methods_group)
        layout.addWidget(data_group)
        layout.addLayout(button_layout)
        
    def load_data(self):
        """Load data from file"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Data File", "", 
            "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)", 
            options=options
        )
        
        if file_path:
            # Load data implementation would go here
            pass
            
    def save_results(self):
        """Save analysis results"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", 
            "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)", 
            options=options
        )
        
        if file_path:
            # Save results implementation would go here
            pass
            
    def generate_table(self):
        """Generate data table based on input parameters"""
        try:
            num_alternatives = int(self.num_alternatives_input.text())
            num_criteria = int(self.num_criteria_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numbers for alternatives and criteria.")
            return
            
        self.data_table.setRowCount(num_alternatives)
        self.data_table.setColumnCount(num_criteria)
        self.data_table.setHorizontalHeaderLabels([f"Criterion {i+1}" for i in range(num_criteria)])
        
        # Fill with default values
        for i in range(num_alternatives):
            for j in range(num_criteria):
                item = QTableWidgetItem(str(1.0))
                self.data_table.setItem(i, j, item)
                
    def analyze(self):
        """Perform MCDA analysis"""
        # Get selected methods
        selected_methods = []
        for method, checkbox in self.method_checkboxes.items():
            if checkbox.isChecked():
                selected_methods.append(method)
                
        if not selected_methods:
            QMessageBox.warning(self, "Error", "Please select at least one method.")
            return
            
        # Get data from table
        data = []
        for i in range(self.data_table.rowCount()):
            row = []
            for j in range(self.data_table.columnCount()):
                item = self.data_table.item(i, j)
                if item and item.text():
                    try:
                        row.append(float(item.text()))
                    except ValueError:
                        row.append(0.0)
                else:
                    row.append(0.0)
            data.append(row)
            
        # Get weights
        try:
            weights_str = self.weights_input.text()
            weights = [float(w.strip()) for w in weights_str.split(',')]
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid weights format. Please enter comma-separated numbers.")
            return
            
        if len(weights) != self.data_table.columnCount():
            QMessageBox.warning(self, "Error", f"Number of weights ({len(weights)}) must match number of criteria ({self.data_table.columnCount()}).")
            return
            
        # Perform analysis (this would call functions from mcda_methods module)
        from mcda_methods import perform_analysis
        results = perform_analysis(data, selected_methods, weights)
        
        # Show results in a new window
        from results_window import ResultsWindow
        results_window = ResultsWindow(data, selected_methods, weights, results)
        results_window.show()
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", "MCDA Analysis Tool\nVersion 1.0")


class ResultsWindow(QWidget):
    """Window to display analysis results"""
    
    def __init__(self, data, methods, inputs, results, parent=None):
        super(ResultsWindow, self).__init__(parent)
        
        self.data = data
        self.methods = methods
        self.inputs = inputs
        self.results = results
        
        self.initUI()
        
    def initUI(self):
        """Initialize the results window UI"""
        self.setWindowTitle("Analysis Results")
        self.setGeometry(150, 150, 1200, 800)
        
        # Apply modern style sheet
        self.setStyleSheet(STYLE_SHEET)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Left side: Original data table
        left_layout = QVBoxLayout()
        
        data_group = QGroupBox("Original Data")
        data_layout = QVBoxLayout(data_group)
        
        self.data_table = QTableWidget()
        self.data_table.setRowCount(len(self.data))
        self.data_table.setColumnCount(len(self.data[0]) if self.data else 0)
        self.data_table.setHorizontalHeaderLabels([f"Criterion {i+1}" for i in range(len(self.data[0]) if self.data else 0)])
        
        for i, row in enumerate(self.data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.data_table.setItem(i, j, item)
        
        data_layout.addWidget(self.data_table)
        left_layout.addWidget(data_group)
        
        # Right side: Results tabs
        right_layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        
        # Add a tab for each method
        for method in self.methods:
            if method in self.results:
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)
                
                results_table = QTableWidget()
                
                # Set up the table based on results
                if isinstance(self.results[method], list) and self.results[method]:
                    if isinstance(self.results[method][0], (list, tuple)):
                        # Results are in table format
                        rows = len(self.results[method])
                        cols = len(self.results[method][0])
                        results_table.setRowCount(rows)
                        results_table.setColumnCount(cols)
                        
                        for i, row in enumerate(self.results[method]):
                            for j, val in enumerate(row):
                                item = QTableWidgetItem(str(val))
                                results_table.setItem(i, j, item)
                    else:
                        # Results are in single column format
                        results_table.setRowCount(len(self.results[method]))
                        results_table.setColumnCount(1)
                        results_table.setHorizontalHeaderLabels(["Rank"])
                        
                        for i, val in enumerate(self.results[method]):
                            item = QTableWidgetItem(str(val))
                            results_table.setItem(i, 0, item)
                
                tab_layout.addWidget(results_table)
                self.tabs.addTab(tab, method)
        
        right_layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        right_layout.addLayout(button_layout)
        
        # Combine layouts
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        self.setLayout(main_layout)