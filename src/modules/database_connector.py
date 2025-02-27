import logging
import sqlite3
from contextlib import contextmanager

class DatabaseConnector:
    _instance = None
    
    def __new__(cls, db_path="sgbd_simulator.db"):
        if cls._instance is None:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
            cls._instance.db_path = str(db_path)
            cls._instance.connection = None
        return cls._instance

    def connect(self) -> None:
        try:
            self.connection = sqlite3.connect(str(self.db_path))  # Utiliser le bon chemin de la BD
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