import sys
import numpy as np
from PyQt5.QtWidgets import *

class MultiCriteriaApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize variables
        self.methods = ['WSR', 'TOPSIS', 'ELECTRA', 'VIKOR']
        self.weights = [0.4, 0.3, 0.3]
        self.concordance_threshold = 0.8
        self.discordance_threshold = 0.2
        self.data = [[8, 7, 6], [7, 7, 7], [6, 7, 8]]

        # Initialize UI
        self.init_ui()
  
    def init_ui(self):
        
        main_layout = QVBoxLayout()

        tabs = QTabWidget()
        wsrTab = QWidget()
        topsisTab = QWidget()

        wsrTab_layout = QVBoxLayout(wsrTab)
        wsrTab_paretotable = QTableWidget()
        wsrTab_settingsGroup = QGroupBox()
        

        topsisTab_layout = QVBoxLayout(topsisTab)

        tabs.addTab(wsrTab, "WSR")
        tabs.addTab(topsisTab, "TOPSIS")

        main_layout.addWidget(tabs)

        self.setLayout(main_layout)
        self.setWindowTitle('Multi-Criteria Assessment')
        self.show()


    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MultiCriteriaApp()
    sys.exit(app.exec_())
