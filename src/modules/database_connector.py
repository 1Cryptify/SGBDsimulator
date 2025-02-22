
from PyQt5.QtWidgets import QMessageBox
import sqlite3

class DatabaseConnector:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        try:
            self.connection = sqlite3.connect('sgbd_simulator.db')
            return True
        except Exception as e:
            return False
