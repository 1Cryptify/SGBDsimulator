import sqlite3
from .database_connector import DatabaseConnector

class SchemaManager:
    def __init__(self, db_path):
        """Initialisation avec connexion à la base de données"""
        self.connector = DatabaseConnector(db_path)
        self.connector.connect()

    def create_table(self, table_name, columns, constraints=None):
        """
        Crée une table avec les colonnes et contraintes spécifiées.
        columns : dict {nom_colonne: type_colonne}
        constraints : list de contraintes SQL (ex: ["PRIMARY KEY(id)", "FOREIGN KEY(user_id) REFERENCES users(id)"])
        """
        try:
            if not isinstance(columns, dict):
                raise ValueError("columns must be a dictionary")
                
            columns_def = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
            if constraints:
                columns_def += ", " + ", ".join(constraints)
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
            
            with self.connector.transaction() as cursor:
                cursor.execute(query)
                # Ajout des métadonnées dans sys_tables
                cursor.execute("""
                    INSERT INTO sys_tables (table_name, description)
                    VALUES (?, ?)
                """, (table_name, f"Table created with {len(columns)} columns"))
                
                table_id = cursor.lastrowid
                
                # Ajout des métadonnées des colonnes
                for col_name, col_type in columns.items():
                    cursor.execute("""
                        INSERT INTO sys_columns (table_id, column_name, data_type, is_nullable)
                        VALUES (?, ?, ?, 1)
                    """, (table_id, col_name, col_type))
                
                # Ajout des contraintes dans sys_constraints
                if constraints:
                    for constraint in constraints:
                        cursor.execute("""
                            INSERT INTO sys_constraints (table_id, constraint_name, constraint_type, constraint_definition)
                            VALUES (?, ?, ?, ?)
                        """, (table_id, f"constraint_{table_name}", "TABLE", constraint))
                
                cursor.execute("""
                    INSERT INTO sys_logs (operation_type, table_name, details)
                    VALUES (?, ?, ?)
                """, ("CREATE_TABLE", table_name, f"Created with {len(columns)} columns"))
                
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de la table {table_name}: {e}")
        except ValueError as e:
            print(f"Erreur de validation: {e}")

    def rename_table(self, old_name, new_name):
        """Renomme une table"""
        with self.connector.transaction() as cursor:
            cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
            cursor.execute("UPDATE sys_tables SET table_name = ?, updated_at = CURRENT_TIMESTAMP WHERE table_name = ?",
                         (new_name, old_name))
            cursor.execute("""
                INSERT INTO sys_logs (operation_type, table_name, details)
                VALUES (?, ?, ?)
            """, ("RENAME_TABLE", old_name, f"Renamed to {new_name}"))

    def add_column(self, table_name, column_name, column_type):
        """Ajoute une colonne à une table existante"""
        with self.connector.transaction() as cursor:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            cursor.execute("SELECT id FROM sys_tables WHERE table_name = ?", (table_name,))
            table_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO sys_columns (table_id, column_name, data_type, is_nullable)
                VALUES (?, ?, ?, 1)
            """, (table_id, column_name, column_type))
            cursor.execute("""
                INSERT INTO sys_logs (operation_type, table_name, details)
                VALUES (?, ?, ?)
            """, ("ADD_COLUMN", table_name, f"Added column {column_name}"))

    def rename_column(self, table_name, old_column, new_column):
        """Renomme une colonne"""
        with self.connector.transaction() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            new_columns = []
            for col in columns_info:
                col_name, col_type = col[1], col[2]
                if col_name == old_column:
                    new_columns.append(f"{new_column} {col_type}")
                else:
                    new_columns.append(f"{col_name} {col_type}")

            new_table_sql = f"""
                CREATE TABLE {table_name}_new ({", ".join(new_columns)});
                INSERT INTO {table_name}_new SELECT * FROM {table_name};
                DROP TABLE {table_name};
                ALTER TABLE {table_name}_new RENAME TO {table_name};
            """
            cursor.executescript(new_table_sql)
            
            cursor.execute("SELECT id FROM sys_tables WHERE table_name = ?", (table_name,))
            table_id = cursor.fetchone()[0]
            cursor.execute("""
                UPDATE sys_columns 
                SET column_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE table_id = ? AND column_name = ?
            """, (new_column, table_id, old_column))
            
            cursor.execute("""
                INSERT INTO sys_logs (operation_type, table_name, details)
                VALUES (?, ?, ?)
            """, ("RENAME_COLUMN", table_name, f"Renamed column {old_column} to {new_column}"))

    def list_tables(self):
        """Retourne la liste des tables de la base de données"""
        with self.connector.transaction() as cursor:
            cursor.execute("SELECT table_name FROM sys_tables")
            return [table[0] for table in cursor.fetchall()]

    def validate_schema(self, table_name):
        """Vérifie la structure d'une table"""
        with self.connector.transaction() as cursor:
            cursor.execute("""
                SELECT c.column_name, c.data_type, c.is_nullable
                FROM sys_tables t
                JOIN sys_columns c ON t.id = c.table_id
                WHERE t.table_name = ?
            """, (table_name,))
            return cursor.fetchall()

    def check_foreign_keys(self):
        """Vérifie si les clés étrangères sont activées"""
        with self.connector.transaction() as cursor:
            cursor.execute("PRAGMA foreign_keys")
            return cursor.fetchone()[0] == 1

    def enable_foreign_keys(self):
        """Active les clés étrangères si elles ne le sont pas"""
        with self.connector.transaction() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON")

    def drop_table(self, table_name):
        """Supprime une table de la base de données"""
        with self.connector.transaction() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute("DELETE FROM sys_tables WHERE table_name = ?", (table_name,))
            cursor.execute("""
                INSERT INTO sys_logs (operation_type, table_name, details)
                VALUES (?, ?, ?)
            """, ("DROP_TABLE", table_name, "Table dropped"))

    def close_connection(self):
        """Ferme la connexion à la base de données"""
        self.connector.close_connection()