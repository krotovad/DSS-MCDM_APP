import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QComboBox, QMainWindow, QApplication, QLabel, QHBoxLayout
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Данные
data = np.array([
    [665, 30.1039, 9.0212, 2.696],
    [37.49, 36.2534, 19.9408, 4.436],
    [27.228, 5.96, 7.846, 2.1203],
    [41.07, 3.3925, 9.0875, 1.88],
    [87.4545, 14.5948, 4.9724, -3.554],
    [74.0925, 5.9645, 4.0124, 0.999],
    [147.2, 25.0565, 6.2261, 1.773],
    [41.1565, 5.6074, 9.33, 1.65],
    [37.724, 8.2933, 6.5044, 1.704],
    [42.0855, 5.8424, 7.368, -2.942],
    [0.409, 0.1017, 8.119, 1.968],
    [40.3862, 1.559, 5.456, 0.666]
])

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.plot()

    def plot(self, criterion_index=0):
        self.ax.clear()
        X = data[:, criterion_index]
        Y = np.prod(data, axis=1)
        Z = np.prod(np.delete(data, criterion_index, axis=1), axis=1)
        self.ax.scatter(X, Y, Z, c='r', marker='o')
        self.ax.set_xlabel(f'Criterion {criterion_index + 1}')
        self.ax.set_ylabel('Product of All Criteria')
        self.ax.set_zlabel('Product of Other Criteria')
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('3D Visualization')
        self.setGeometry(50, 50, 800, 600)

        self.main_widget = QtWidgets.QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.canvas = PlotCanvas(self.main_widget)
        self.main_layout.addWidget(self.canvas)

        # Верхний макет для исследуемого критерия
        self.top_layout = QHBoxLayout()
        self.criterion_label = QLabel('Исследуемый критерий:', self.main_widget)
        self.combo_box = QComboBox(self.main_widget)
        self.combo_box.addItems([f'Criterion {i+1}' for i in range(data.shape[1])])
        self.combo_box.currentIndexChanged.connect(self.update_plot)

        self.top_layout.addWidget(self.criterion_label)
        self.top_layout.addWidget(self.combo_box)

        # Нижний макет для остальных критериев
        self.bottom_layout = QHBoxLayout()
        self.remaining_criteria_label = QLabel('', self.main_widget)
        self.bottom_layout.addWidget(self.remaining_criteria_label)

        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addLayout(self.bottom_layout)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.update_plot(0)  # Initial update to set labels

    def update_plot(self, index):
        self.canvas.plot(index)
        remaining_criteria = [f'Criterion {i+1}' for i in range(data.shape[1]) if i != index]
        self.remaining_criteria_label.setText(f'Зависимость мультипликативной функции решения от комбинации критериев {{ {", ".join(remaining_criteria)} }}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
