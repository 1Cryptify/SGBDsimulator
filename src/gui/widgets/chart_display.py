from PyQt5 import QtWidgets, QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ChartDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ChartDisplay, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def plot(self, x_data, y_data, chart_type='line'):
        """Plot the chart based on the provided data."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if chart_type == 'line':
            ax.plot(x_data, y_data, label='Line Chart')
        elif chart_type == 'bar':
            ax.bar(x_data, y_data, label='Bar Chart')
        elif chart_type == 'pie':
            ax.pie(y_data, labels=x_data, autopct='%1.1f%%', startangle=90)

        ax.legend()
        self.canvas.draw()

    def clear_chart(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()
