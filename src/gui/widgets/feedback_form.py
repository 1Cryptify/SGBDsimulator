from PyQt5 import QtWidgets, QtCore

class FeedbackForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(FeedbackForm, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.feedback_label = QtWidgets.QLabel("Your Feedback:", self)
        self.feedback_input = QtWidgets.QTextEdit(self)

        self.rating_label = QtWidgets.QLabel("Rate your experience:", self)
        self.rating_input = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.rating_input.setRange(1, 5)

        self.submit_button = QtWidgets.QPushButton("Submit", self)

        self.layout.addWidget(self.feedback_label)
        self.layout.addWidget(self.feedback_input)
        self.layout.addWidget(self.rating_label)
        self.layout.addWidget(self.rating_input)
        self.layout.addWidget(self.submit_button)

        self.setStyleSheet("""
            QLabel {
                padding: 5px;
            }
            QTextEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QSlider {
                margin: 10px 0;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        self.submit_button.clicked.connect(self.submit_feedback)

    def submit_feedback(self):
        """Submit the feedback."""
        feedback = self.feedback_input.toPlainText()
        rating = self.rating_input.value()
        # Logic to handle feedback submission goes here
        print(f"Feedback submitted: {feedback}, Rating: {rating}")
