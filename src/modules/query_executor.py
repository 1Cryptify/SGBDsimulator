import logging
from .database_connector import DatabaseConnector, DatabaseConnector
from typing import List, Tuple

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QueryExecutor:
    def __init__(self, db_path: str):
        """Initialisation avec le chemin de la base de données SQLite"""
        self.connector = DatabaseConnector(db_path)
        self.connector.connect()
        self.connection = self.connector.get_connection() 
    
    def connect(self):
        """Établit la connexion à la base de données"""
        self.connector.connect()

    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Exécute une requête SQL avec gestion des erreurs et optimisation"""
        with self.connector.transaction() as cursor:
            logging.info(f"Exécution de la requête : {query}")
            cursor.execute(query, params)
            results = cursor.fetchall()
            logging.info(f"Requête exécutée avec succès. Nombre de résultats : {len(results)}.")
            return results
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Exécute une requête d'insertion et retourne l'ID du dernier enregistrement inséré"""
        with self.connector.transaction() as cursor:
            logging.info(f"Exécution de la requête d'insertion : {query}")
            cursor.execute(query, params)
            inserted_id = cursor.lastrowid
            logging.info(f"Insertion réussie. ID inséré : {inserted_id}")
            return inserted_id

    def get_column_names(self) -> List[Tuple[str, str]]:
        """Retourne les noms et types des colonnes de la dernière requête exécutée"""
        with self.connector.transaction() as cursor:
            return cursor.description

    def get_table_columns(self, table_name: str) -> List[str]:
        """Retourne la liste des noms de colonnes d'une table"""
        query = f"PRAGMA table_info({table_name})"
        results = self.execute_query(query)
        return [row[1] for row in results]  # Column name is at index 1

    def close(self): 
        """Ferme la connexion à la base de données"""
        self.connector.close_connection() 
