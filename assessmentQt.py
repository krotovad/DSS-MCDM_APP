from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QListWidget, 
                             QTextEdit, QStackedWidget, QLabel, QListWidgetItem)
from PyQt5.QtCore import Qt

class AssessmentWindow(QDialog):
    def __init__(self):
        super(AssessmentWindow, self).__init__()

        # Main Layout
        layout = QHBoxLayout()

        # 1. Multicriterial Assessment Methods Section
        self.methods_list = QListWidget()
        self.methods_list.setSelectionMode(QAbstractItemView.MultiSelection)

        methods = {
            "MCDA Methods": ["TOPSIS", "WSR", "ELECTRE", "VIKOR"]
        }

        for category, methods in methods.items():
            label = QListWidgetItem(category)
            label.setFlags(Qt.ItemIsEnabled)
            self.methods_list.addItem(label)
            for method in methods:
                self.methods_list.addItem(QListWidgetItem(method))

        self.methods_list.itemSelectionChanged.connect(self.method_selected)

        # 2. Method Info Widget
        self.method_info = QTextEdit()
        self.method_info.setPlaceholderText("Method Info will be displayed here...")
        self.method_info.setReadOnly(True)  # Make it read-only
        self.method_info.setFontItalic(True)  # Set the font to Italic

        # 3. Stacked Widget for Dynamic Sections
        self.dynamic_section = QStackedWidget()
        # Example of adding widgets to the stacked section
        self.dynamic_section.addWidget(QLabel("Dynamic Content for TOPSIS"))
        self.dynamic_section.addWidget(QLabel("Dynamic Content for WSR"))
        # ... Add other widgets as needed ...

        # Arrange Layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.methods_list)
        left_layout.addWidget(self.dynamic_section)

        layout.addLayout(left_layout)
        layout.addWidget(self.method_info)
        
        self.setLayout(layout)

    def method_selected(self):
        # Get Selected Items
        selected_items = self.methods_list.selectedItems()

        if selected_items:
            selected_method = selected_items[-1].text()  # Consider the last selected item
            self.method_info.setPlainText(f"Info about {selected_method}")
            # Here, instead of setting plain text, you can set the relevant info about the method
            # Change the displayed widget in dynamic section based on the selected method
            # Example: self.dynamic_section.setCurrentIndex(index_of_the_widget_for_selected_method)
        else:
            self.method_info.clear()  # Clear the info if no item is selected
