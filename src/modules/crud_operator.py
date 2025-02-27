import logging
from .database_connector import DatabaseConnector
from typing import List, Dict, Any

class CRUDOperator:
    def __init__(self, db_path: str):
        """Initialisation avec le chemin de la base de données SQLite"""
        self.connector = DatabaseConnector(db_path)
        self.connector.connect()

    def create(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insère un nouvel enregistrement dans la table spécifiée."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        with self.connector.transaction() as cursor:
            cursor.execute(query, tuple(data.values()))
            inserted_id = cursor.lastrowid
            logging.info(f"Enregistrement inséré avec succès dans {table_name}. ID: {inserted_id}")
            return inserted_id

    def read(self, table_name: str, conditions: str = '', params: tuple = ()) -> List[Dict[str, Any]]:
        """Récupère les enregistrements de la table spécifiée."""
        query = f"SELECT * FROM {table_name} {conditions}"
        
        with self.connector.transaction() as cursor:
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            logging.info(f"{len(results)} enregistrements récupérés de {table_name}.")
            return results

    def update(self, table_name: str, data: Dict[str, Any], conditions: str, params: tuple) -> None:
        """Met à jour les enregistrements dans la table spécifiée."""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {conditions}"
        
        with self.connector.transaction() as cursor:
            cursor.execute(query, tuple(data.values()) + params)
            logging.info(f"Enregistrements mis à jour dans {table_name}.")

    def delete(self, table_name: str, conditions: str, params: tuple) -> None:
        """Supprime les enregistrements de la table spécifiée."""
        query = f"DELETE FROM {table_name} WHERE {conditions}"
        
        with self.connector.transaction() as cursor:
            cursor.execute(query, params)
            logging.info(f"Enregistrements supprimés de {table_name}.")

    def close(self) -> None:
        """Ferme la connexion à la base de données."""
        self.connector.close_connection()
