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
                ordinal_position INTEGER,
                is_primary_key BOOLEAN DEFAULT 0,
                is_foreign_key BOOLEAN DEFAULT 0,
                referenced_table TEXT,
                referenced_column TEXT,
                is_unique BOOLEAN DEFAULT 0,
                is_indexed BOOLEAN DEFAULT 0,
                check_constraint TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES sys_tables(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_indexes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                index_name TEXT NOT NULL,
                column_name TEXT NOT NULL,
                is_unique BOOLEAN DEFAULT 0,
                is_primary BOOLEAN DEFAULT 0,
                index_type TEXT DEFAULT 'BTREE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES sys_tables(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sys_constraints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                constraint_name TEXT NOT NULL,
                constraint_type TEXT NOT NULL CHECK (constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'NOT NULL')),
                column_name TEXT NOT NULL,
                referenced_table TEXT,
                referenced_column TEXT,
                check_clause TEXT,
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
            ('sys_constraints', 'SYSTEM', 'Table containing metadata about constraints'),
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
                
                # Get the table_id for the system table
                cursor.execute("SELECT id FROM sys_tables WHERE table_name = ?", (table_name,))
                table_id = cursor.fetchone()[0]
                
                # Get column information for system tables
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                
                # Get foreign key information
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                fk_info = {col[3]: (col[2], col[4]) for col in cursor.fetchall()}
                
                # Get index information
                cursor.execute(f"PRAGMA index_list({table_name})")
                index_info = cursor.fetchall()
                
                # Insert system columns metadata with enhanced information
                for position, col in enumerate(columns_info, 1):
                    column_name = col[1]
                    is_pk = bool(col[5])  # pk flag from PRAGMA table_info
                    is_fk = column_name in fk_info
                    ref_table = fk_info[column_name][0] if is_fk else None
                    ref_column = fk_info[column_name][1] if is_fk else None
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO sys_columns (
                            table_id, column_name, data_type, is_nullable,
                            column_default, ordinal_position, is_primary_key,
                            is_foreign_key, referenced_table, referenced_column,
                            character_maximum_length
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        table_id, column_name, col[2], not col[3],
                        col[4], position, is_pk, is_fk, ref_table,
                        ref_column, None
                    ))
                    
                    # Add constraint information
                    if is_pk:
                        cursor.execute("""
                            INSERT OR IGNORE INTO sys_constraints (
                                table_id, constraint_name, constraint_type,
                                column_name
                            )
                            VALUES (?, ?, ?, ?)
                        """, (
                            table_id,
                            f"pk_{table_name}_{column_name}",
                            "PRIMARY KEY",
                            column_name
                        ))
                    
                    if is_fk:
                        cursor.execute("""
                            INSERT OR IGNORE INTO sys_constraints (
                                table_id, constraint_name, constraint_type,
                                column_name, referenced_table, referenced_column
                            )
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            table_id,
                            f"fk_{table_name}_{column_name}",
                            "FOREIGN KEY",
                            column_name,
                            ref_table,
                            ref_column
                        ))
                
                # Add index information
                for idx in index_info:
                    cursor.execute(f"PRAGMA index_info({idx[1]})")
                    idx_columns = cursor.fetchall()
                    for idx_col in idx_columns:
                        cursor.execute("""
                            INSERT OR IGNORE INTO sys_indexes (
                                table_id, index_name, column_name,
                                is_unique, is_primary
                            )
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            table_id,
                            idx[1],
                            columns_info[idx_col[1]][1],
                            bool(idx[2]),
                            idx[1].startswith('sqlite_autoindex')
                        ))

    def _log_operation(self, operation_type: str, table_name: str, status: str = 'SUCCESS', message: str = None, details: str = None) -> None:
        """Enregistre une opération dans sys_logs"""
        query = """
            INSERT INTO sys_logs (operation_type, table_name, status, message, details) 
            VALUES (?, ?, ?, ?, ?)
        """
        with self.connector.transaction() as cursor:
            cursor.execute(query, (operation_type, table_name, status, message, details))

    def _update_table_metadata(self, table_name: str) -> None:
        """Met à jour les métadonnées de la table"""
        with self.connector.transaction() as cursor:
            # Mise à jour de sys_tables
            cursor.execute("""
                UPDATE sys_tables 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE table_name = ?
            """, (table_name,))
            
            # Récupération de l'ID de la table
            cursor.execute("SELECT id FROM sys_tables WHERE table_name = ?", (table_name,))
            table_id = cursor.fetchone()[0]
            
            # Suppression des anciennes métadonnées
            cursor.execute("DELETE FROM sys_columns WHERE table_id = ?", (table_id,))
            cursor.execute("DELETE FROM sys_indexes WHERE table_id = ?", (table_id,))
            cursor.execute("DELETE FROM sys_constraints WHERE table_id = ?", (table_id,))
            
            # Récupération des informations sur les colonnes
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            # Récupération des clés étrangères
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            fk_info = {col[3]: (col[2], col[4]) for col in cursor.fetchall()}
            
            # Récupération des index
            cursor.execute(f"PRAGMA index_list({table_name})")
            index_info = cursor.fetchall()
            
            # Mise à jour des colonnes et contraintes
            for position, col in enumerate(columns_info, 1):
                column_name = col[1]
                is_pk = bool(col[5])
                is_fk = column_name in fk_info
                ref_table = fk_info[column_name][0] if is_fk else None
                ref_column = fk_info[column_name][1] if is_fk else None
                
                cursor.execute("""
                    INSERT INTO sys_columns (
                        table_id, column_name, data_type, is_nullable,
                        column_default, ordinal_position, is_primary_key,
                        is_foreign_key, referenced_table, referenced_column
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    table_id, column_name, col[2], not col[3],
                    col[4], position, is_pk, is_fk, ref_table,
                    ref_column
                ))
                
                if is_pk:
                    cursor.execute("""
                        INSERT INTO sys_constraints (
                            table_id, constraint_name, constraint_type,
                            column_name
                        )
                        VALUES (?, ?, ?, ?)
                    """, (
                        table_id,
                        f"pk_{table_name}_{column_name}",
                        "PRIMARY KEY",
                        column_name
                    ))
                
                if is_fk:
                    cursor.execute("""
                        INSERT INTO sys_constraints (
                            table_id, constraint_name, constraint_type,
                            column_name, referenced_table, referenced_column
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        table_id,
                        f"fk_{table_name}_{column_name}",
                        "FOREIGN KEY",
                        column_name,
                        ref_table,
                        ref_column
                    ))
            
            # Mise à jour des index
            for idx in index_info:
                cursor.execute(f"PRAGMA index_info({idx[1]})")
                idx_columns = cursor.fetchall()
                for idx_col in idx_columns:
                    cursor.execute("""
                        INSERT INTO sys_indexes (
                            table_id, index_name, column_name,
                            is_unique, is_primary
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        table_id,
                        idx[1],
                        columns_info[idx_col[1]][1],
                        bool(idx[2]),
                        idx[1].startswith('sqlite_autoindex')
                    ))

    def create(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insère un nouvel enregistrement dans la table spécifiée."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            with self.connector.transaction() as cursor:
                cursor.execute("SELECT table_type FROM sys_tables WHERE table_name = ?", (table_name,))
                result = cursor.fetchone()
                if not result:
                    cursor.execute("""
                        INSERT INTO sys_tables (table_name, table_type, description)
                        VALUES (?, 'USER', ?)
                    """, (table_name, f"User created table: {table_name}"))
                
                cursor.execute(query, tuple(data.values()))
                inserted_id = cursor.lastrowid
                self._log_operation(
                    "INSERT",
                    table_name,
                    'SUCCESS',
                    f"Record inserted successfully with ID: {inserted_id}"
                )
                self._update_table_metadata(table_name)
                return inserted_id
        except Exception as e:
            self._log_operation(
                "INSERT",
                table_name,
                'ERROR',
                str(e)
            )
            raise

    def read(self, table_name: str, conditions: str = '', params: tuple = ()) -> List[Dict[str, Any]]:
        """Récupère les enregistrements de la table spécifiée."""
        query = f"SELECT * FROM {table_name} {conditions}"
        
        try:
            with self.connector.transaction() as cursor:
                cursor.execute(query, params)
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                self._log_operation(
                    "SELECT",
                    table_name,
                    'SUCCESS',
                    f"Retrieved {len(results)} records"
                )
                return results
        except Exception as e:
            self._log_operation(
                "SELECT",
                table_name,
                'ERROR',
                str(e)
            )
            raise

    def update(self, table_name: str, data: Dict[str, Any], conditions: str, params: tuple) -> None:
        """Met à jour les enregistrements dans la table spécifiée."""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {conditions}"
        
        try:
            with self.connector.transaction() as cursor:
                cursor.execute(query, tuple(data.values()) + params)
                affected_rows = cursor.rowcount
                self._log_operation(
                    "UPDATE",
                    table_name,
                    'SUCCESS',
                    f"Updated {affected_rows} records",
                    f"Conditions: {conditions}"
                )
                self._update_table_metadata(table_name)
        except Exception as e:
            self._log_operation(
                "UPDATE",
                table_name,
                'ERROR',
                str(e)
            )
            raise

    def delete(self, table_name: str, conditions: str, params: tuple) -> None:
        """Supprime les enregistrements de la table spécifiée."""
        query = f"DELETE FROM {table_name} WHERE {conditions}"
        
        try:
            with self.connector.transaction() as cursor:
                cursor.execute(query, params)
                affected_rows = cursor.rowcount
                self._log_operation(
                    "DELETE",
                    table_name,
                    'SUCCESS',
                    f"Deleted {affected_rows} records",
                    f"Conditions: {conditions}"
                )
                self._update_table_metadata(table_name)
        except Exception as e:
            self._log_operation(
                "DELETE",
                table_name,
                'ERROR',
                str(e)
            )
            raise

    def close(self) -> None:
        """Ferme la connexion à la base de données."""
        self.connector.close_connection()
