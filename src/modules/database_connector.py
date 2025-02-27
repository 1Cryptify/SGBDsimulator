import logging
import sqlite3
from contextlib import contextmanager

class DatabaseConnector:
    def __init__(self, db_path="default.db"):
        self.db_path = db_path
        self.connection = None  

    def connect(self) -> None:
        try:
            self.connection = sqlite3.connect(self.db_path)  # Utiliser le bon chemin de la BD
            logging.info("Connexion réussie à la base de données.")
        except Exception as e:
            logging.error(f"Erreur de connexion : {e}")
            raise e

    def get_connection(self):
        """Retourne la connexion SQLite. Si la connexion n'est pas établie, elle sera créée."""
        if self.connection is None: 
            logging.info("Tentative de connexion à la base de données.")
            self.connect() 
        return self.connection

    @contextmanager
    def transaction(self):
        """Gère une transaction avec commit et rollback."""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            logging.error(f"Erreur dans la transaction : {e}")
            raise e
        finally:
            cursor.close()

    def close_connection(self):
        """Ferme la connexion à la base de données."""
        if self.connection:
            self.connection.close()
            logging.info("Connexion fermée.")
