import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CenteredWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Centered Window')
        self.resize(300, 200)  # Resize the window to the desired size
        
    def showEvent(self, event):
        self.center_on_screen()
        super().showEvent(event)

    def center_on_screen(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())


app = QApplication(sys.argv)
window = CenteredWindow()
window.show()
sys.exit(app.exec_())