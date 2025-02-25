from PyQt5.QtWidgets import QMessageBox
import sqlite3

class DatabaseConnector:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None  

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)  # Utiliser le bon chemin de la BD
            return True
        except Exception as e:
            return False

    def get_connection(self):
        """Retourne la connexion SQLite."""
        if self.connection is None:
            self.connect()
        return self.connection
