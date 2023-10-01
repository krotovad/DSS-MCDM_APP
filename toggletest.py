from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QTabWidget

app = QApplication([])

window = QWidget()
layout = QVBoxLayout(window)

# Create a QTabWidget instance
tab_widget = QTabWidget()

tab_names = ['Tab 1', 'Tab 2', 'Tab 3']  # The list you are going to read

for name in tab_names:
    tab = QWidget()  # Create a new tab widget
    tab_layout = QVBoxLayout(tab)  # Create a layout for the tab
    tab_layout.addWidget(QLabel(f"Content in {name}"))  # Add a label to the tab
    tab_widget.addTab(tab, name)  # Add the tab to the QTabWidget with the name from the list

layout.addWidget(tab_widget)

window.show()

app.exec_()
