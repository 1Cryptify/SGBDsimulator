from PyQt5 import QtWidgets, QtCore

class DataTableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DataTableWidget, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # Create table widget with better display
        self.table = QtWidgets.QTableWidget(self)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        
        # Add search/filter functionality
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.filter_table)
        
        # Add row count label
        self.row_count_label = QtWidgets.QLabel()
        self.update_row_count()
        
        # Layout assembly
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.row_count_label)
        
        # Style
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 8px;
            }
        """)

    def set_headers(self, headers):
        """Set the column headers for the table."""
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)

    def add_row(self, row_data):
        """Add a row of data to the table."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        for column, data in enumerate(row_data):
            item = QtWidgets.QTableWidgetItem()
            
            # Handle different data types
            if isinstance(data, (int, float)):
                item.setData(QtCore.Qt.DisplayRole, data)
                item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            elif isinstance(data, bool):
                item.setCheckState(QtCore.Qt.Checked if data else QtCore.Qt.Unchecked)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            else:
                item.setText(str(data) if data is not None else "")
            
            self.table.setItem(row_position, column, item)
        
        self.update_row_count()

    def clear(self):
        """Clear all rows from the table."""
        self.table.setRowCount(0)
        self.update_row_count()

    def get_selected_row_data(self):
        """Return the data of the selected row as a dictionary."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            row_data = {}
            for column in range(self.table.columnCount()):
                header = self.table.horizontalHeaderItem(column).text()
                item = self.table.item(selected_row, column)
                row_data[header] = item.text() if item else None
            return row_data
        return None

    def set_data(self, data):
        """Set all data in the table at once."""
        self.clear()
        
        if not data:
            return
            
        # If data is a list of dicts, extract headers
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
            self.set_headers(headers)
            for row_dict in data:
                self.add_row([row_dict[header] for header in headers])
        else:
            for row_data in data:
                self.add_row(row_data)
                
        self.update_row_count()

    def filter_table(self, text):
        """Filter table rows based on search text."""
        for row in range(self.table.rowCount()):
            row_hidden = True
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if item and text.lower() in item.text().lower():
                    row_hidden = False
                    break
            self.table.setRowHidden(row, row_hidden)
        
        self.update_row_count()

    def update_row_count(self):
        """Update the row count label."""
        visible_rows = sum(1 for row in range(self.table.rowCount()) 
                         if not self.table.isRowHidden(row))
        total_rows = self.table.rowCount()
        self.row_count_label.setText(
            f"Affichage de {visible_rows} ligne(s) sur {total_rows} au total"
        )
