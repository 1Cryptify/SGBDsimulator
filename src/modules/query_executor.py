import logging
from .database_connector import DatabaseConnector, DatabaseConnector
from typing import List, Tuple, Dict
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QueryExecutor:
    def __init__(self, db_path: str):
        """Initialisation avec le chemin de la base de données SQLite"""
        self.connector = DatabaseConnector(db_path)
        self.connector.connect()
        self.connection = self.connector.get_connection()
        self._create_system_tables()
    
    def _create_system_tables(self):
        """Crée les tables système nécessaires"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS sys_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL UNIQUE,
                table_type TEXT NOT NULL CHECK (table_type IN ('SYSTEM', 'USER')),
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
                column_default TEXT,
                character_maximum_length INTEGER,
                numeric_precision INTEGER,
                numeric_scale INTEGER,
                is_identity BOOLEAN DEFAULT 0,
                is_computed BOOLEAN DEFAULT 0,
                ordinal_position INTEGER,
                is_hidden BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                FOREIGN KEY (table_id) REFERENCES sys_tables(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_indexes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                index_name TEXT NOT NULL,
                is_unique BOOLEAN DEFAULT 0,
                is_primary BOOLEAN DEFAULT 0,
                is_clustered BOOLEAN DEFAULT 0,
                index_type TEXT NOT NULL,
                filter_definition TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES sys_tables(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_index_columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_id INTEGER,
                column_id INTEGER,
                key_ordinal INTEGER,
                is_descending BOOLEAN DEFAULT 0,
                is_included_column BOOLEAN DEFAULT 0,
                FOREIGN KEY (index_id) REFERENCES sys_indexes(id) ON DELETE CASCADE,
                FOREIGN KEY (column_id) REFERENCES sys_columns(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_constraints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                constraint_name TEXT NOT NULL,
                constraint_type TEXT NOT NULL CHECK (constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'NOT NULL', 'DEFAULT')),
                constraint_definition TEXT NOT NULL,
                is_enabled BOOLEAN DEFAULT 1,
                is_trusted BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referenced_table_id INTEGER,
                FOREIGN KEY (table_id) REFERENCES sys_tables(id) ON DELETE CASCADE,
                FOREIGN KEY (referenced_table_id) REFERENCES sys_tables(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_constraint_columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                constraint_id INTEGER,
                column_id INTEGER,
                referenced_column_id INTEGER,
                ordinal_position INTEGER,
                FOREIGN KEY (constraint_id) REFERENCES sys_constraints(id) ON DELETE CASCADE,
                FOREIGN KEY (column_id) REFERENCES sys_columns(id) ON DELETE CASCADE,
                FOREIGN KEY (referenced_column_id) REFERENCES sys_columns(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                table_name TEXT NOT NULL,
                operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'SUCCESS',
                message TEXT,
                user_id TEXT,
                details TEXT
            )
            """
        ]
        
        system_tables = [
            ('sys_tables', 'SYSTEM', 'Table containing metadata about all tables'),
            ('sys_columns', 'SYSTEM', 'Table containing metadata about columns'),
            ('sys_indexes', 'SYSTEM', 'Table containing metadata about indexes'),
            ('sys_index_columns', 'SYSTEM', 'Table containing metadata about index columns'),
            ('sys_constraints', 'SYSTEM', 'Table containing metadata about constraints'),
            ('sys_constraint_columns', 'SYSTEM', 'Table containing metadata about constraint columns'),
            ('sys_logs', 'SYSTEM', 'Table containing system operation logs')
        ]
        
        with self.connector.transaction() as cursor:
            for query in queries:
                cursor.execute(query)
            
            # Insert system tables metadata
            for table_name, table_type, description in system_tables:
                cursor.execute("""
                    INSERT OR IGNORE INTO sys_tables (table_name, table_type, description)
                    VALUES (?, ?, ?)
                """, (table_name, table_type, description))
                
                # Get table schema information and populate sys_columns
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_info = cursor.fetchall()
                
                # Get the table_id
                cursor.execute("SELECT id FROM sys_tables WHERE table_name = ?", (table_name,))
                table_id = cursor.fetchone()[0]
                
                # Insert column information
                for col in table_info:
                    cursor.execute("""
                        INSERT OR IGNORE INTO sys_columns (
                            table_id, column_name, data_type, 
                            is_nullable, column_default, ordinal_position
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (table_id, col[1], col[2], not col[3], col[4], col[0]))
    
    def _log_operation(self, operation_type: str, table_name: str, details: str = None):
        """Enregistre une opération dans sys_logs"""
        with self.connector.transaction() as cursor:
            cursor.execute("""
                INSERT INTO sys_logs (operation_type, table_name, details)
                VALUES (?, ?, ?)
            """, (operation_type, table_name, details))

    def _register_table(self, table_name: str, columns_info: List[Tuple]):
        """Enregistre une nouvelle table dans sys_tables et sys_columns"""
        with self.connector.transaction() as cursor:
            cursor.execute("""
                INSERT INTO sys_tables (table_name, table_type)
                VALUES (?, 'USER')
            """)
            table_id = cursor.lastrowid
            
            for pos, col_info in enumerate(columns_info, 1):
                cursor.execute("""
                    INSERT INTO sys_columns (
                        table_id, column_name, data_type, 
                        is_nullable, column_default, ordinal_position
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (table_id, col_info[0], col_info[1], col_info[2], col_info[3], pos))

    def connect(self):
        """Établit la connexion à la base de données"""
        self.connector.connect()

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Exécute une requête SQL avec gestion des erreurs et optimisation"""
        query_upper = query.upper().strip()
        
        with self.connector.transaction() as cursor:
            # Analyse du type de requête
            if query_upper.startswith('CREATE TABLE'):
                # Extraction du nom de la table et des colonnes
                match = re.match(r'CREATE TABLE (?:IF NOT EXISTS )?([\w_]+)', query, re.IGNORECASE)
                if match:
                    table_name = match.group(1)
                    cursor.execute(query, params)
                    # Récupération des informations sur les colonnes
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns_info = [(row[1], row[2], not row[3], row[4]) for row in cursor.fetchall()]
                    self._register_table(table_name, columns_info)
                    self._log_operation('CREATE_TABLE', table_name, query)
                return []
            else:
                cursor.execute(query, params)
                
                if query_upper.startswith(('INSERT', 'UPDATE', 'DELETE')):
                    return []
                
                columns = [description[0] for description in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                logging.info(f"Requête exécutée avec succès.")
                return results if results else []
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Exécute une requête d'insertion et retourne l'ID du dernier enregistrement inséré"""
        with self.connector.transaction() as cursor:
            match = re.match(r'INSERT INTO ([\w_]+)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                cursor.execute(query, params)
                self._log_operation('INSERT', table_name, query)
                inserted_id = cursor.lastrowid
                logging.info(f"Insertion réussie. ID inséré : {inserted_id}")
                return inserted_id

    def get_column_names(self) -> List[Tuple[str, str]]:
        """Retourne les noms et types des colonnes de la dernière requête exécutée"""
        with self.connector.transaction() as cursor:
            return cursor.description or []

    def get_table_columns(self, table_name: str) -> List[str]:
        """Retourne la liste des noms de colonnes d'une table"""
        query = f"PRAGMA table_info({table_name})"
        with self.connector.transaction() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return [row[1] for row in results] if results else []

    def close(self): 
        """Ferme la connexion à la base de données"""
        self.connector.close_connection()