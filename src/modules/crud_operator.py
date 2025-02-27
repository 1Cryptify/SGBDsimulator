import logging
from .database_connector import DatabaseConnector
from typing import List, Dict, Any

class CRUDOperator:
    def __init__(self, db_path: str):
        """Initialisation avec le chemin de la base de données SQLite"""
        self.connector = DatabaseConnector(db_path)
        self.connector.connect()
        self._create_system_tables()

    def _create_system_tables(self):
        """Crée les tables système nécessaires"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS sys_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL UNIQUE,
                table_type TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                column_name TEXT NOT NULL,
                data_type TEXT NOT NULL,
                is_nullable BOOLEAN DEFAULT 1,
                default_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES sys_tables(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_indexes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                index_name TEXT NOT NULL,
                is_unique BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES sys_tables(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_constraints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                constraint_name TEXT NOT NULL,
                constraint_type TEXT NOT NULL,
                constraint_definition TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES sys_tables(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                table_name TEXT NOT NULL,
                operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                details TEXT
            )
            """
        ]
        
        with self.connector.transaction() as cursor:
            for query in queries:
                cursor.execute(query)

    def _log_operation(self, operation_type: str, table_name: str, details: str = None) -> None:
        """Enregistre une opération dans sys_logs"""
        query = "INSERT INTO sys_logs (operation_type, table_name, details) VALUES (?, ?, ?)"
        with self.connector.transaction() as cursor:
            cursor.execute(query, (operation_type, table_name, details))

    def _update_table_metadata(self, table_name: str) -> None:
        """Met à jour les métadonnées de la table"""
        with self.connector.transaction() as cursor:
            # Mise à jour de sys_tables
            cursor.execute("UPDATE sys_tables SET updated_at = CURRENT_TIMESTAMP WHERE table_name = ?", (table_name,))
            
            # Récupération des informations sur les colonnes
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            # Mise à jour de sys_columns
            table_id_query = "SELECT id FROM sys_tables WHERE table_name = ?"
            cursor.execute(table_id_query, (table_name,))
            table_id = cursor.fetchone()[0]
            
            # Suppression des anciennes entrées
            cursor.execute("DELETE FROM sys_columns WHERE table_id = ?", (table_id,))
            
            # Ajout des nouvelles entrées
            for col in columns_info:
                cursor.execute("""
                    INSERT INTO sys_columns (table_id, column_name, data_type, is_nullable, default_value)
                    VALUES (?, ?, ?, ?, ?)
                """, (table_id, col[1], col[2], not col[3], col[4]))

    def create(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insère un nouvel enregistrement dans la table spécifiée."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        with self.connector.transaction() as cursor:
            cursor.execute(query, tuple(data.values()))
            inserted_id = cursor.lastrowid
            self._log_operation("INSERT", table_name, f"ID: {inserted_id}")
            self._update_table_metadata(table_name)
            logging.info(f"Enregistrement inséré avec succès dans {table_name}. ID: {inserted_id}")
            return inserted_id

    def read(self, table_name: str, conditions: str = '', params: tuple = ()) -> List[Dict[str, Any]]:
        """Récupère les enregistrements de la table spécifiée."""
        query = f"SELECT * FROM {table_name} {conditions}"
        
        with self.connector.transaction() as cursor:
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self._log_operation("SELECT", table_name, f"Nombre d'enregistrements: {len(results)}")
            logging.info(f"{len(results)} enregistrements récupérés de {table_name}.")
            return results

    def update(self, table_name: str, data: Dict[str, Any], conditions: str, params: tuple) -> None:
        """Met à jour les enregistrements dans la table spécifiée."""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {conditions}"
        
        with self.connector.transaction() as cursor:
            cursor.execute(query, tuple(data.values()) + params)
            self._log_operation("UPDATE", table_name, f"Conditions: {conditions}")
            self._update_table_metadata(table_name)
            logging.info(f"Enregistrements mis à jour dans {table_name}.")

    def delete(self, table_name: str, conditions: str, params: tuple) -> None:
        """Supprime les enregistrements de la table spécifiée."""
        query = f"DELETE FROM {table_name} WHERE {conditions}"
        
        with self.connector.transaction() as cursor:
            cursor.execute(query, params)
            self._log_operation("DELETE", table_name, f"Conditions: {conditions}")
            self._update_table_metadata(table_name)
            logging.info(f"Enregistrements supprimés de {table_name}.")

    def close(self) -> None:
        """Ferme la connexion à la base de données."""
        self.connector.close_connection()