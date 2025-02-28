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
                    INSERT INTO sys_tables (table_name, table_type, description)
                    VALUES (?, ?, ?)
                """, (table_name, 'USER', f"Table created with {len(columns)} columns"))
                
                table_id = cursor.lastrowid
                
                # Récupération des informations complètes sur les colonnes
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_info = cursor.fetchall()
                
                # Ajout de toutes les colonnes dans sys_columns
                for col_info in table_info:
                    cursor.execute("""
                        INSERT INTO sys_columns (
                            table_id, column_name, data_type, 
                            is_nullable, ordinal_position, is_system,
                            default_value, max_length, is_identity,
                            is_computed, is_hidden
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        table_id, col_info[1], col_info[2],
                        1 if col_info[3] == 0 else 0, col_info[0] + 1,
                        0, col_info[4], None, 0, 0, 0
                    ))
                
                # Gestion des index et contraintes
                if constraints:
                    for constraint in constraints:
                        constraint_upper = constraint.upper()
                        if "PRIMARY KEY" in constraint_upper:
                            constraint_type = "PRIMARY KEY"
                            # Création d'un index automatique pour la clé primaire
                            index_name = f"pk_{table_name}"
                            cursor.execute("""
                                INSERT INTO sys_indexes (
                                    table_id, index_name, is_unique, 
                                    is_primary, index_type, columns
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (table_id, index_name, 1, 1, "BTREE", constraint))
                        elif "FOREIGN KEY" in constraint_upper:
                            constraint_type = "FOREIGN KEY"
                            # Extraction des informations de la clé étrangère
                            fk_info = constraint.split("REFERENCES")
                            referenced_table = fk_info[1].strip().split("(")[0].strip()
                            cursor.execute("""
                                INSERT INTO sys_indexes (
                                    table_id, index_name, is_unique, 
                                    is_primary, index_type, columns
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (table_id, f"fk_{table_name}", 0, 0, "BTREE", constraint))
                        elif "UNIQUE" in constraint_upper:
                            constraint_type = "UNIQUE"
                            cursor.execute("""
                                INSERT INTO sys_indexes (
                                    table_id, index_name, is_unique, 
                                    is_primary, index_type, columns
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (table_id, f"uk_{table_name}", 1, 0, "BTREE", constraint))
                        else:
                            constraint_type = "CHECK" if "CHECK" in constraint_upper else "NOT NULL"
                            
                        cursor.execute("""
                            INSERT INTO sys_constraints (
                                table_id, constraint_name, constraint_type,
                                constraint_definition, is_enabled, is_system_generated,
                                referenced_table_id, referenced_columns
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            table_id, f"constraint_{table_name}_{constraint_type.lower()}",
                            constraint_type, constraint, 1, 0, None, None
                        ))
                
                cursor.execute("""
                    INSERT INTO sys_logs (operation_type, table_name, status, details)
                    VALUES (?, ?, ?, ?)
                """, ("CREATE_TABLE", table_name, "SUCCESS", f"Created with {len(columns)} columns"))
                
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
            # Mise à jour des index et contraintes
            cursor.execute("UPDATE sys_indexes SET index_name = replace(index_name, ?, ?) WHERE table_id = (SELECT id FROM sys_tables WHERE table_name = ?)",
                         (old_name, new_name, new_name))
            cursor.execute("UPDATE sys_constraints SET constraint_name = replace(constraint_name, ?, ?) WHERE table_id = (SELECT id FROM sys_tables WHERE table_name = ?)",
                         (old_name, new_name, new_name))
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
            
            # Récupération des informations de la nouvelle colonne
            cursor.execute(f"PRAGMA table_info({table_name})")
            col_info = [col for col in cursor.fetchall() if col[1] == column_name][0]
            
            cursor.execute("""
                INSERT INTO sys_columns (
                    table_id, column_name, data_type, is_nullable,
                    ordinal_position, is_system, default_value,
                    max_length, is_identity, is_computed, is_hidden
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                table_id, column_name, column_type, 1,
                col_info[0] + 1, 0, None, None, 0, 0, 0
            ))
            
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
            
            # Mise à jour de sys_columns
            cursor.execute("""
                UPDATE sys_columns 
                SET column_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE table_id = ? AND column_name = ?
            """, (new_column, table_id, old_column))
            
            # Mise à jour des index et contraintes qui référencent cette colonne
            cursor.execute("""
                UPDATE sys_indexes 
                SET columns = replace(columns, ?, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE table_id = ? AND columns LIKE ?
            """, (old_column, new_column, table_id, f"%{old_column}%"))
            
            cursor.execute("""
                UPDATE sys_constraints 
                SET constraint_definition = replace(constraint_definition, ?, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE table_id = ? AND constraint_definition LIKE ?
            """, (old_column, new_column, table_id, f"%{old_column}%"))
            
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
                SELECT c.column_name, c.data_type, c.is_nullable,
                       c.is_system, c.default_value, c.max_length,
                       c.is_identity, c.is_computed, c.is_hidden
                FROM sys_tables t
                JOIN sys_columns c ON t.id = c.table_id
                WHERE t.table_name = ?
                ORDER BY c.ordinal_position
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
            # Récupération de l'ID de la table
            cursor.execute("SELECT id FROM sys_tables WHERE table_name = ?", (table_name,))
            table_id = cursor.fetchone()[0]
            
            # Suppression des métadonnées associées
            cursor.execute("DELETE FROM sys_columns WHERE table_id = ?", (table_id,))
            cursor.execute("DELETE FROM sys_indexes WHERE table_id = ?", (table_id,))
            cursor.execute("DELETE FROM sys_constraints WHERE table_id = ?", (table_id,))
            
            # Suppression de la table
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute("DELETE FROM sys_tables WHERE table_name = ?", (table_name,))
            
            cursor.execute("""
                INSERT INTO sys_logs (operation_type, table_name, details)
                VALUES (?, ?, ?)
            """, ("DROP_TABLE", table_name, "Table and all related metadata dropped"))

    def close_connection(self):
        """Ferme la connexion à la base de données"""
        self.connector.close_connection()