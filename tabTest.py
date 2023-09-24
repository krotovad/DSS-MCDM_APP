import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Tab Example")
        self.setGeometry(100, 100, 600, 400)

        self.initUI()

    def initUI(self):
        self.tab_widget = QTabWidget()

        # Create Tabs
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        # Setup Tabs
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()

        # Add Tabs to QTabWidget
        self.tab_widget.addTab(self.tab1, "Tab 1")
        self.tab_widget.addTab(self.tab2, "Tab 2")
        self.tab_widget.addTab(self.tab3, "Tab 3")

        self.setCentralWidget(self.tab_widget)

    def setup_tab1(self):
        layout = QVBoxLayout()
        label = QLabel("This is Tab 1")
        layout.addWidget(label)
        self.tab1.setLayout(layout)

    def setup_tab2(self):
        layout = QVBoxLayout()
        label = QLabel("This is Tab 2")
        layout.addWidget(label)
        self.tab2.setLayout(layout)

    def setup_tab3(self):
        layout = QVBoxLayout()
        label = QLabel("This is Tab 3")
        layout.addWidget(label)
        self.tab3.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = App()
    mainWin.show()
    sys.exit(app.exec_())