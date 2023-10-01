import csv
import sys
import openpyxl
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class AssessmentWindow(QWidget):
    def __init__(self, data):
        super(AssessmentWindow, self).__init__()
        self.data = data
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
        self.additional_input = QTextEdit(self)
        self.additional_input.setText("No additional inputs needed")
        grid_layout.addWidget(self.additional_input, 1, 0, 1, 2)  # Spanning the widget across both columns

    def display_info(self):
        info = ""
        additional_section_visible = False
        additional_inputs_needed = False

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

        for index in range(self.method_list.count()):
            item = self.method_list.item(index)
            widget = self.method_list.itemWidget(item)
            if widget and isinstance(widget, QCheckBox) and widget.isChecked():
                method = widget.text()
                if method in method_descriptions:
                    info += method_descriptions[method] + "\n\n"
                if method in ['TOPSIS', 'WSR', 'ELECTRE', 'VIKOR']:
                    additional_inputs_needed = True

        self.info_widget.setText(info)
        if additional_inputs_needed:
            self.additional_input.setText("Additional inputs are needed for the selected method(s).")
        else:
            self.additional_input.setText("No additional inputs needed")


class CalculateAlternativesWindow(QDialog):
    def __init__(self):
        super(CalculateAlternativesWindow, self).__init__()

        layout = QVBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_pressed)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)
        self.save_pressed_flag = False

    def save_pressed(self):
        print("Save pressed in Calculate Alternatives window")
        self.save_pressed_flag = True
        self.close()

def open_input_alternatives_window(main_window):
    main_window.hide()
    window = InputAlternativesWindow(main_window)
    window.exec_()
    main_window.show()

class InputAlternativesWindow(QDialog):
    def __init__(self):
        super(InputAlternativesWindow, self).__init__()

        self.data = [['' for _ in range(3)] for _ in range(3)]
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        
        # Setup Buttons
        self.setup_buttons()
        
        # Setup Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setRowCount(3)
        self.table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.table.itemSelectionChanged.connect(self.handle_item_selection)
        
        # Place the table and button_layout in a horizontal layout
        h_layout = QVBoxLayout()
        h_layout.addLayout(self.button_layout)  # Add button_layout (import and add/remove buttons) to the horizontal layout
        h_layout.addWidget(self.table)  # Add table to the horizontal layout
        
        self.main_layout.addLayout(h_layout)  # Add horizontal layout to the main layout
        self.main_layout.addLayout(self.save_cancel_layout)  # Add save_cancel_layout below the horizontal layout
        self.main_layout.addStretch(1)
        self.adjustSize()
        #self.adjust_dialog_size()

    def setup_buttons(self):
        # Create Buttons
        self.import_csv_button = QPushButton("Import from CSV", self)
        self.import_xlsx_button = QPushButton("Import from XLSX", self)
        self.add_remove_column_button = QPushButton("Add Column", self)
        self.add_remove_row_button = QPushButton("Add Row", self)

        # Connect Buttons
        self.import_csv_button.clicked.connect(self.import_csv)
        self.import_xlsx_button.clicked.connect(self.import_xlsx)
        self.add_remove_column_button.clicked.connect(self.add_column)
        self.add_remove_row_button.clicked.connect(self.add_row)

        # Button Layout for import and add/remove buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.import_csv_button)
        self.button_layout.addWidget(self.import_xlsx_button)
        self.button_layout.addWidget(self.add_remove_column_button)
        self.button_layout.addWidget(self.add_remove_row_button)

        # Save and Cancel Buttons
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Button Layout for Save and Cancel
        self.save_cancel_layout = QHBoxLayout()  # Changed to QHBoxLayout to put buttons side by side
        self.save_cancel_layout.addStretch(1)
        self.save_cancel_layout.addWidget(self.save_button)
        self.save_cancel_layout.addWidget(self.cancel_button)


    def adjust_dialog_size(self):
        width = self.table.verticalHeader().width() + 4  # for border
        for i in range(self.table.columnCount()):
            width += self.table.columnWidth(i)  # width of each column

        height = self.table.horizontalHeader().height() + 4
        for i in range(self.table.rowCount()):
            height += self.table.rowHeight(i)  # height of each row

        max_height = 1000  # example value, adjust as needed
        max_width = 2000  # example value, adjust as needed
        
        width = min(width, max_width)
        height = min(height, max_height)
        
        self.resize(width, height)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reset_buttons()
            self.table.clearSelection()
        else:
            super(InputAlternativesWindow, self).keyPressEvent(event)
    
    def mousePressEvent(self, event):
        # Detecting if a widget under the cursor is a QPushButton, if not it's assumed to be empty space
        widget = QApplication.widgetAt(QCursor.pos())
        if not isinstance(widget, QPushButton):
            self.reset_buttons()
            self.table.clearSelection()
        super(InputAlternativesWindow, self).mousePressEvent(event)
    
    def reset_buttons(self):
        self.add_remove_row_button.setText("Add Row")
        self.add_remove_row_button.disconnect()
        self.add_remove_row_button.clicked.connect(self.add_row)

        self.add_remove_column_button.setText("Add Column")
        self.add_remove_column_button.disconnect()
        self.add_remove_column_button.clicked.connect(self.add_column)
    
    def handle_item_selection(self):
        selected_indices = self.table.selectedIndexes()
        if selected_indices:
            rows = set(index.row() for index in selected_indices)
            columns = set(index.column() for index in selected_indices)
            if len(rows) == 1:
                self.add_remove_row_button.setText("Delete Row")
                self.add_remove_row_button.disconnect()
                self.add_remove_row_button.clicked.connect(self.delete_row)
            else:
                self.add_remove_row_button.setText("Add Row")
                self.add_remove_row_button.disconnect()
                self.add_remove_row_button.clicked.connect(self.add_row)

            if len(columns) == 1:
                self.add_remove_column_button.setText("Delete Column")
                self.add_remove_column_button.disconnect()
                self.add_remove_column_button.clicked.connect(self.delete_column)
            else:
                self.add_remove_column_button.setText("Add Column")
                self.add_remove_column_button.disconnect()
                self.add_remove_column_button.clicked.connect(self.add_column)

    def import_csv(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if filePath:
            with open(filePath, 'r', newline='', encoding='utf-8') as file:
                self.data = []
                reader = csv.reader(file, delimiter=';')
                for row in reader:
                    # check if row was split considering ';' as delimiter
                    if len(row) == 1:
                        # try to split row considering ',' as delimiter
                        row = row[0].split(',')
                    self.data.append([cell.strip() for cell in row])
                    
                # Remove the header row
                self.data = self.data[1:]
                self.update_table()

    def import_xlsx(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open XLSX File", "", "XLSX Files (*.xlsx);;All Files (*)", options=options)
        if filePath:
            book = openpyxl.load_workbook(filePath, read_only=True)
            sheet = book.active
            self.data = [[cell for cell in row] for row in sheet.iter_rows(values_only=True)][1:]
            self.update_table()

    def update_table(self):
        self.table.clear()
        self.table.setRowCount(len(self.data))  # limit to 10 rows
        self.table.setColumnCount(len(self.data[0]))  # limit to 15 columns
        for row in range(len(self.data)):
            for col in range(len(self.data[row])):
                item = QTableWidgetItem(str(self.data[row][col]))
                item.setTextAlignment(Qt.AlignCenter)  # Set text alignment to center
                if row < 10 and col < 15:  # only add to the table if within limits
                    self.table.setItem(row, col, item)
        #self.adjust_dialog_size()
        self.adjustSize()


    def add_column(self):
        for row_data in self.data:
            row_data.append('')
        self.update_table()
        #self.adjust_dialog_size()

    def add_row(self):
        self.data.append(['' for _ in range(self.table.columnCount())])
        self.update_table()
        #self.adjust_dialog_size()

    def delete_column(self):
        col_index = self.table.currentColumn()
        if col_index > -1:
            for row_data in self.data:
                del row_data[col_index]
            self.update_table()
        #self.adjust_dialog_size()

    def delete_row(self):
        row_index = self.table.currentRow()
        if row_index > -1:
            del self.data[row_index]
            self.update_table()
        #self.adjust_dialog_size()
    
    def get_data(self):
        return self.data

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

class CalculateAlternativesWindow(QWidget):
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

class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.initUI()
        self.dbwindow = None
        self.alternatives_data = None
        self.assessment_window = None

    def initUI(self):
        self.setWindowTitle('Main Layout')
        layout = QHBoxLayout(self.central_widget)

        calculate_button = QPushButton("Calculate Alternatives")
        calculate_button.clicked.connect(self.calculate_alternatives)

        input_button = QPushButton("Input Alternatives")
        input_button.clicked.connect(self.input_alternatives)

        self.assessment_button = QPushButton("Multicriterial Assessment")
        self.assessment_button.setEnabled(False)
        self.assessment_button.clicked.connect(self.assessment)

        calculate_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        input_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.assessment_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(calculate_button)
        layout.addWidget(input_button)
        layout.addWidget(self.assessment_button)

        self.show()

    def calculate_alternatives(self):
        print("Calculating Alternatives...")
        self.dbwindow = CalculateAlternativesWindow()
        self.dbwindow.show()

    def input_alternatives(self):
        print("Inputting Alternatives...")
        self.hide()
        window = InputAlternativesWindow()
        if window.exec_() == QDialog.Accepted:  # QDialog.Accepted is returned when 'Save' is pressed
            self.alternatives_data = window.get_data()  # Store table data as state
            self.assessment_button.setEnabled(True)
        self.show()

    def assessment(self):
        print("Performing Multicriterial Assessment...")
        self.hide()
        self.assessment_window = AssessmentWindow(self.alternatives_data)
        self.assessment_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
