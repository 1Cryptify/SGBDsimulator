import sqlite3
import logging
from typing import List, Tuple, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QueryExecutor:
    def __init__(self, db_path: str):
        """Initialisation avec le chemin de la base de données SQLite"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            logging.info("Connexion réussie à la base de données.")
        except sqlite3.Error as e:
            logging.error(f"Erreur de connexion : {e}")
            raise e

    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Exécute une requête SQL avec gestion des erreurs et optimisation"""
        if not self.cursor:
            raise Exception("La connexion n'est pas établie. Appelez connect() avant d'exécuter une requête.")
        
        try:
            logging.info(f"Exécution de la requête : {query}")
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            logging.info(f"Requête exécutée avec succès. Nombre de résultats : {len(results)}.")
            return results
        except sqlite3.Error as e:
            logging.error(f"Erreur d'exécution de la requête : {e}")
            return []
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Exécute une requête d'insertion et retourne l'ID du dernier enregistrement inséré"""
        if not self.cursor:
            raise Exception("La connexion n'est pas établie. Appelez connect() avant d'exécuter une requête.")
        
        try:
            logging.info(f"Exécution de la requête d'insertion : {query}")
            self.cursor.execute(query, params)
            self.connection.commit()
            inserted_id = self.cursor.lastrowid
            logging.info(f"Insertion réussie. ID inséré : {inserted_id}")
            return inserted_id
        except sqlite3.Error as e:
            logging.error(f"Erreur d'insertion : {e}")
            return -1

    def close(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            logging.info("Connexion fermée.")

    def optimize_query(self, query: str) -> str:
        """Optimisation basique des requêtes SQL (exemple pour SELECT avec LIMIT et INDEX)"""
        if "SELECT" in query.upper():
            query = query.strip() + " LIMIT 100" 
        return query
