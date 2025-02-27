from PyQt5 import QtWidgets, QtCore

class DataTableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DataTableWidget, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableWidget(self)
        self.layout.addWidget(self.table)
        self.table.setStyleSheet("QTableWidget { border: 1px solid #ccc; border-radius: 5px; }"
                                 "QHeaderView::section { background-color: #007BFF; color: white; padding: 5px; }"
                                 "QTableWidget::item { padding: 5px; }"
                                 "QTableWidget::item:hover { background-color: #f0f0f0; }")

    def set_headers(self, headers):
        """Set the column headers for the table."""
        self.table.setColumnCount(len(headers))
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #007BFF; color: white; }")
        self.table.setHorizontalHeaderLabels(headers)

    def add_row(self, row_data):
        """Add a row of data to the table."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for column, data in enumerate(row_data):
            self.table.setItem(row_position, column, QtWidgets.QTableWidgetItem(str(data)))

    def clear(self):
        """Clear all rows from the table."""
        self.table.setRowCount(0)

    def get_selected_row_data(self):
        """Return the data of the selected row."""
        selected_items = self.table.selectedItems()
        if selected_items:
            return [item.text() for item in selected_items]
        return None
    def set_data(self, data):
            """Set all data in the table at once.
            
            Args:
                data: List of lists/tuples containing row data
            """
            self.clear()
            for row_data in data:
                self.add_row(row_data)
