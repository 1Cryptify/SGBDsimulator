from .database_connector import DatabaseConnector
from .database_connector import DatabaseConnector

class SchemaManager:
    def __init__(self, db_path):
        """Initialisation avec connexion à la base de données"""
        self.connector = DatabaseConnector(db_path)
        self.connection = self.connector.get_connection() 

    def create_table(self, table_name, columns, constraints=None):
        """
        Crée une table avec les colonnes et contraintes spécifiées.
        columns : dict {nom_colonne: type_colonne}
        constraints : list de contraintes SQL (ex: ["PRIMARY KEY(id)", "FOREIGN KEY(user_id) REFERENCES users(id)"])
        """
        try:
            columns_def = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
            if constraints:
                columns_def += ", " + ", ".join(constraints)
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
            with self.connector.transaction() as cursor:
                cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de la table {table_name}: {e}")

    def rename_table(self, old_name, new_name):
        """Renomme une table"""
        query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
        with self.connector.transaction() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def add_column(self, table_name, column_name, column_type):
        """Ajoute une colonne à une table existante"""
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        self.cursor.execute(query)
        self.connection.commit()

    def rename_column(self, table_name, old_column, new_column):
        """
        Renomme une colonne (SQLite ne supporte pas directement ALTER COLUMN, donc on recrée la table)
        """
        new_columns = []
        with self.connector.transaction() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = self.cursor.fetchall()
        
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
        self.cursor.executescript(new_table_sql)
        self.connection.commit()

    def list_tables(self):
        """Retourne la liste des tables de la base de données"""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        with self.connector.transaction() as cursor:
            cursor.execute(query)
        return [table[0] for table in self.cursor.fetchall()]

    def validate_schema(self, table_name):
        """Vérifie la structure d'une table"""
        query = f"PRAGMA table_info({table_name})"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def check_foreign_keys(self):
        """Vérifie si les clés étrangères sont activées"""
        query = "PRAGMA foreign_keys;"
        self.cursor.execute(query)
        return self.cursor.fetchone()[0] == 1

    def enable_foreign_keys(self):
        """Active les clés étrangères si elles ne le sont pas"""
        with self.connector.transaction() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON;")
        self.connection.commit()

    def drop_table(self, table_name):
        """Supprime une table de la base de données"""
        query = f"DROP TABLE IF EXISTS {table_name}"
        with self.connector.transaction() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def close_connection(self):
        """Ferme la connexion à la base de données"""
        self.connector.close_connection()
