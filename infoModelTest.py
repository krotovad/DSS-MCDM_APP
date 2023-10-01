import sqlite3
import sys
from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem,
                             QVBoxLayout, QWidget, QFileDialog, QMenu)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush

class TableGraphicsItem(QGraphicsRectItem):
    def __init__(self, tableName, columns, parent=None):
        super(TableGraphicsItem, self).__init__(parent)

        self.setBrush(QBrush(Qt.lightGray))
        self.setRect(QRectF(0, 0, 150, 30 + 20 * len(columns)))

        title = QGraphicsTextItem(tableName, self)
        title.setPos(10, 5)

        for i, (colName, colType) in enumerate(columns):
            textItem = QGraphicsTextItem(f"{colName} ({colType})", self)
            textItem.setPos(10, 35 + i * 20)

    def contextMenuEvent(self, event):
        menu = QMenu()
        action1 = menu.addAction("Action 1")
        action2 = menu.addAction("Action 2")
        selectedAction = menu.exec_(event.screenPos())
        if selectedAction == action1:
            print("Action 1 selected")
        elif selectedAction == action2:
            print("Action 2 selected")


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)

        self.layout.addWidget(self.view)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('DB Infological Model')
        self.show()

        self.openFileNameDialog()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open SQLite Database", "", "SQLite Databases (*.db);;All Files (*)", options=options)

        if fileName:
            self.loadTables(fileName)

    def loadTables(self, dbFile):
        conn = sqlite3.connect(dbFile)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        x = 10
        y = 10
        max_height = 0
        for table in tables:
            tableName = table[0]
            cursor.execute(f"PRAGMA table_info({tableName});")
            columns = [(col[1], col[2]) for col in cursor.fetchall()]
            tableItem = TableGraphicsItem(tableName, columns)
            tableItem.setPos(x, y)
            self.scene.addItem(tableItem)

            rect = tableItem.rect()
            max_height = max(max_height, rect.height())
            y += max_height + 20  # 20 is the vertical space between tables

            if y > self.view.height() - max_height - 20:
                y = 10
                x += rect.width() + 50  # 50 is the horizontal space between tables

        conn.close()


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
