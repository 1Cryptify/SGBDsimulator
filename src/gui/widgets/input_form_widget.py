from PyQt5 import QtWidgets, QtCore

class InputFormWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, form_style=None, button_style=None):
        super(InputFormWidget, self).__init__(parent)
        self.layout = QtWidgets.QGridLayout(self)
        self.setStyleSheet(form_style or "background-color: #f0f0f0; padding: 10px;")

        self.fields = {}
        self.submit_button = QtWidgets.QPushButton("Submit", self)
        self.submit_button.setStyleSheet(button_style or "background-color: #4CAF50; color: white; padding: 10px; border: none; border-radius: 5px;")
        self.submit_button.clicked.connect(self.submit)

        self.layout.addWidget(self.submit_button, 0, 0, 1, 2)

    def add_field(self, label_text, field_type="text", placeholder="", validator=None):
        """Add a new input field to the form."""
        label = QtWidgets.QLabel(label_text, self)
        if field_type == "text":
            field = QtWidgets.QLineEdit(self)
        elif field_type == "number":
            field = QtWidgets.QLineEdit(self)
            field.setValidator(QtWidgets.QDoubleValidator(0.0, 10000.0, 2))  # Example range and precision
        elif field_type == "date":
            field = QtWidgets.QDateEdit(self)
            field.setCalendarPopup(True)
        else:
            field = QtWidgets.QLineEdit(self)

        field.setPlaceholderText(placeholder)
        if validator:
            field.setValidator(validator)

        field.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        self.fields[label_text] = field
        row_position = len(self.fields)
        self.layout.addWidget(label, row_position, 0)
        self.layout.addWidget(field, row_position, 1)

    def submit(self):
        """Handle the submission of the form."""
        data = {label: field.text() if isinstance(field, QtWidgets.QLineEdit) else field.date().toString(QtCore.Qt.ISODate) for label, field in self.fields.items()}
        # Call the custom submit handler if defined
        if hasattr(self, 'submit_handler'):
            self.submit_handler(data)
        print("Submitted Data:", data)  # Replace with actual handling logic
        self.clear_fields()

    def clear_fields(self):
        """Clear all input fields."""
        for field in self.fields.values():
            if isinstance(field, QtWidgets.QLineEdit):
                field.clear()
            elif isinstance(field, QtWidgets.QDateEdit):
                field.setDate(QtCore.QDate.currentDate())

    def set_submit_handler(self, handler):
        """Set a custom submit handler."""
        self.submit_button.clicked.disconnect()
        self.submit_button.clicked.connect(handler)

    def get_input(self):
        """Get the input from the first field in the form."""
        if self.fields:
            first_field = next(iter(self.fields.values()))
            if isinstance(first_field, QtWidgets.QLineEdit):
                return first_field.text()
            elif isinstance(first_field, QtWidgets.QDateEdit):
                return first_field.date().toString(QtCore.Qt.ISODate)
        return ""