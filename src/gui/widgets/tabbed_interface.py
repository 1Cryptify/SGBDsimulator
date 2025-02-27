from PyQt5 import QtWidgets, QtCore

class TabbedInterface(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(TabbedInterface, self).__init__(parent)
        self.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ccc; }
            QTabBar::tab { background: #f0f0f0; padding: 10px; }
            QTabBar::tab:selected { background: #007BFF; color: white; }
            QTabBar::tab:hover { background: #e0e0e0; }
        """)

    def add_tab(self, title, widget):
        """Add a new tab with the specified title and widget."""
        self.addTab(widget, title)

    def remove_tab(self, index):
        """Remove the tab at the specified index."""
        self.removeTab(index)

    def clear_tabs(self):
        """Clear all tabs."""
        self.clear()
