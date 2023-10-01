import sqlite3
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#filename = None

class ClickableTextItem(QGraphicsTextItem):
    def __init__(self, text, parent=None, list_widget1=None, list_widget2=None, filename = None):
        super().__init__(text, parent)
        self.setAcceptHoverEvents(True)
        self.filename = filename
        print(f"list_widget2 in __init__: {list_widget2}")
        self.list_widget2 = list_widget2
        print(f"self.list_widget2 in __init__: {self.list_widget2}")
        
        # Set Flags
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        # Colors
        self.default_color = QColor(Qt.lightGray)  # Default color
        self.selected_color = QColor(Qt.darkGray)  # Color when selected

        # Initially set to default color
        self.current_color = self.default_color
        self.is_clicked = False  # Initially set to False
        
        # Reference to the list widget
        self.list_widget1 = list_widget1
        self.list_widget2 = list_widget2
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(11)

    def boundingRect(self):
        return super().boundingRect()  # Should return the correct bounding rect.

    @staticmethod
    def get_related_attributes(attribute_name, table_name, filename):
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        # Check if the attribute is a key in the given table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        is_key = any(col[1] == attribute_name and col[5] for col in columns)  # col[5] is pk column in PRAGMA output

        within_table_attributes = []
        within_database_attributes = []
        if is_key:
            # Within the same table: List all non-key attributes
            within_table_attributes.extend([col[1] for col in columns if not col[5]])  # col[5] is pk column in PRAGMA output

            # Within the database: List all key attributes of other tables that have direct relations to the selected table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                table = table[0]
                if table == table_name:  # skip the given table
                    continue
                
                print(f"Examining table: {table}")  # Debugging line
                
                cursor.execute(f"PRAGMA foreign_key_list({table})")
                foreign_keys = cursor.fetchall()
                
                for fk in foreign_keys:
                    ref_table = fk[2]  # Reference table
                    ref_attribute = fk[3]  # Reference attribute (from column)
                    
                    print(f"ref_table: {ref_table}, ref_attribute: {ref_attribute}")  # Debugging line
                    
                    if ref_table == table_name and ref_attribute == attribute_name:
                        print(f"Match Found! Examining Columns of table: {table}")  # Debugging line
                        cursor.execute(f"PRAGMA table_info({table})")
                        table_columns = cursor.fetchall()
                        for col in table_columns:
                            is_pk = col[5]  # col[5] is pk column in PRAGMA output
                            col_name = col[1]  # col[1] is the name column in PRAGMA output
                            if is_pk:
                                print(f"Adding: {col_name} to within_database_attributes")  # Debugging line
                                within_database_attributes.append(col_name)
        else:
            # If not a key, only list all attributes from the same table (both key and non-key)
            within_table_attributes.extend([col[1] for col in columns])

        connection.close()
        print(is_key, within_table_attributes, within_database_attributes)
        return is_key, within_table_attributes, within_database_attributes
    
    def populate_related_attributes(self):
        # Get the reference to the second list widget from the main app or another suitable place.
        print("populate_related_attributes called")  # Debugging line
        second_list_widget = self.list_widget2
        
        print(f"self.list_widget2 in populate_related_attributes: {self.list_widget2}")
        second_list_widget = self.list_widget2
        print(second_list_widget)
        if second_list_widget is not None:
            print("Second list widget found")  # Debugging line
            second_list_widget.clear()
            
            # Retrieve the parent_table object using the parentItem() method.
            parent_table = self.parentItem()
            
            if parent_table:
                print("parent_table found")  # Debugging line
                attribute_name = self.toPlainText().split(" ")[0]  # Extract attribute name from displayed text
                table_name = parent_table.tableName  # Replace with the actual way to get table name from parent_table object
                
                # Get the related attributes by calling the function
                print(f"Calling get_related_attributes with attribute_name={attribute_name}, table_name={table_name}")  # Debugging line
                try:
                    is_key, within_table_attributes, within_database_attributes = ClickableTextItem.get_related_attributes(attribute_name, table_name, self.filename)
                except Exception as e:
                    print(f"Error in calling get_related_attributes: {str(e)}")

                # If the attribute is a key, populate the widget with related attributes
                print(f"is_key={is_key}, within_table_attributes={within_table_attributes}, within_database_attributes={within_database_attributes}")  # Debugging line
                if is_key:
                    second_list_widget.addItem("Within Table:")
                    for attribute in within_table_attributes:
                        second_list_widget.addItem(f"  {attribute}")

                    second_list_widget.addItem("Within Database:")
                    for attribute in within_database_attributes:
                        second_list_widget.addItem(f"  {attribute}")
                else:
                    # If not a key, just add the 'Within Table' category
                    second_list_widget.addItem("Within Table:")
                    for attribute in within_table_attributes:
                        second_list_widget.addItem(f"  {attribute}")


    def mousePressEvent(self, event):
        if self.is_clicked:
            self.is_clicked = False
            self.current_color = self.default_color
            self.remove_from_list()
            self.populate_related_attributes()
        else:
            self.is_clicked = True
            self.current_color = self.selected_color
            self.add_to_list()
            self.populate_related_attributes()

        self.update()  # trigger repaint
        super().mousePressEvent(event)

    def add_to_list(self):
        if self.list_widget1 is None:
            print("list_widget1 is None")
        else:
            print("list_widget1 is not None")
            print(f"Adding {self.toPlainText()} to the list")
            self.list_widget1.addItem(self.toPlainText())

    def remove_from_list(self):
        if self.list_widget1 is None:
            print("list_widget is None")
        else:
            print("list_widget is not None")
            print(f"Removing {self.toPlainText()} from the list")
            items = self.list_widget1.findItems(self.toPlainText(), Qt.MatchExactly)
            for item in items:
                row = self.list_widget1.row(item)
                self.list_widget1.takeItem(row)

    
    def paint(self, painter, option, widget=None):
        # Draw background rectangle
        painter.fillRect(self.boundingRect(), self.current_color)
        super().paint(painter, option, widget)


class RelationGraphicsItem(QGraphicsLineItem):
    def __init__(self, tableItem1, tableItem2, parent=None):
        super().__init__(parent)
        
        self.tableItem1 = tableItem1
        self.tableItem2 = tableItem2
                
        pen = QPen(QBrush(Qt.lightGray), 1)
        self.setPen(pen)

        line = QLineF(tableItem1.sceneBoundingRect().center(), tableItem2.sceneBoundingRect().center())
        self.setLine(line)
        
        tableItem1.relations.append(self)
        tableItem2.relations.append(self)

        self.setZValue(5)  # Lines at the bottom
        self.relations = []
    
class TableGraphicsItem(QGraphicsRectItem):
    def __init__(self, tableName, columns, parent=None, list_widget1=None, list_widget2=None, filename = None):
        super().__init__(parent)
        
        self.tableName = tableName
        self.columns = columns
        self.relations = []
        self.setZValue(9) # Tables just below the titles

        self.setBrush(QBrush(Qt.gray))  # Set to gray or your preferred color
        self.setRect(QRectF(0, 0, 150, 30 + 20 * len(columns)))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        title_bg = QGraphicsRectItem(0, 0, 150, 30, self)
        title_bg.setBrush(QBrush(Qt.lightGray))
        title_bg.setZValue(10)  # Table titles on top
        
        title = QGraphicsTextItem(tableName, self)
        title.setPos(10, 5)
        title.setZValue(10)  # Table titles on top
        
        for i, (colName, colType) in enumerate(columns):
            textItem = ClickableTextItem(f"{colName} ({colType})", self, list_widget1=list_widget1, list_widget2=list_widget2, filename = filename)
            textItem.setPos(10, 35 + i * 20)
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:  # Notice the change here
            self.update_relations()

        return super().itemChange(change, value)

    def update_relations(self):
        for relation in self.relations:
            rect1 = self.sceneBoundingRect()
            rect2 = relation.tableItem2.sceneBoundingRect() if relation.tableItem1 == self else relation.tableItem1.sceneBoundingRect()

            center1 = rect1.center()
            center2 = rect2.center()

            line = QLineF(center1, center2)

            p1_intersect = self.calculate_intersection(rect1, line)
            p2_intersect = self.calculate_intersection(rect2, line)

            if p1_intersect and p2_intersect:
                new_line = QLineF(p1_intersect, p2_intersect)
                relation.setLine(new_line)
    
    def calculate_intersection(self, rect, line):
        # Generate lines for each edge of the rectangle
        lines = [
            QLineF(rect.topLeft(), rect.topRight()),
            QLineF(rect.topRight(), rect.bottomRight()),
            QLineF(rect.bottomRight(), rect.bottomLeft()),
            QLineF(rect.bottomLeft(), rect.topLeft()),
        ]

        for rect_line in lines:
            intersection_point = QPointF()
            # Find the intersection point between the rectangle edge and the line
            result = line.intersect(rect_line, intersection_point)
            if result == QLineF.BoundedIntersection:
                return intersection_point

        return None

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Main Layout
        main_layout = QHBoxLayout(self)
        
        # Left Widget for Graphics View
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        left_layout.addWidget(self.view)
        
        # Right Widget for ListWidgets
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # First ListWidget and its GroupBox
        self.table_list1 = QListWidget()
        self.table_list1.setStyleSheet("background-color: #F0F0F0;")
        list_group_box1 = QGroupBox("Selected criteria:")
        list_group_box1.setLayout(QVBoxLayout())
        list_group_box1.layout().addWidget(self.table_list1)
        right_layout.addWidget(list_group_box1)
        
        # Second ListWidget and its GroupBox
        self.table_list2 = QListWidget()
        self.table_list2.setStyleSheet("background-color: #F0F0F0;")
        list_group_box2 = QGroupBox("Suggested criteria")
        list_group_box2.setLayout(QVBoxLayout())
        list_group_box2.layout().addWidget(self.table_list2)
        right_layout.addWidget(list_group_box2)

        #Button for continuing
        continueButton = QPushButton("Continue")
        right_layout.addWidget(continueButton)
        
        # Add Left and Right Widgets to Main Layout
        main_layout.addWidget(left_widget, 2)  # GraphicsView will take 2 parts of the available space
        main_layout.addWidget(right_widget, 1)  # ListWidgets will take 1 part of the available space
        
        # Window Setup
        self.setGeometry(100, 100, 1300, 600)  # Adjusted the window width
        self.setWindowTitle('DB Infological Model')
        self.show()
        
        # Load Tables
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
        
        tableItems = {}
        x = 10
        y = 10
        max_height = 0
        for table in tables:
            tableName = table[0]
            cursor.execute(f"PRAGMA table_info({tableName});")
            columns = [(col[1], col[2]) for col in cursor.fetchall()]
            tableItem = TableGraphicsItem(tableName, columns, list_widget1=self.table_list1, list_widget2=self.table_list2, filename=dbFile)
            tableItem.setPos(x, y)
            self.scene.addItem(tableItem)
            tableItems[tableName] = tableItem
            
            rect = tableItem.rect()
            max_height = max(max_height, rect.height())
            y += max_height + 20
            
            if y > self.view.height() - max_height - 20:
                y = 10
                x += rect.width() + 50
        
        for tableName, tableItem in tableItems.items():
            cursor.execute(f"PRAGMA foreign_key_list({tableName});")
            for relation in cursor.fetchall():
                referencedTable = relation[2]
                if referencedTable in tableItems:
                    lineItem = RelationGraphicsItem(tableItem, tableItems[referencedTable])
                    
                    self.scene.addItem(lineItem)
                    tableItem.relations = getattr(tableItem, 'relations', [])
                    tableItem.relations.append(lineItem)
        conn.close()
        
    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.setResizeAnchor(QGraphicsView.NoAnchor)
        oldPos = self.view.mapToScene(event.pos())
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.view.scale(zoomFactor, zoomFactor)
        newPos = self.view.mapToScene(event.pos())
        delta = newPos - oldPos
        self.view.translate(delta.x(), delta.y())

def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
