import unittest
import sqlite3
from src.modules.schema_manager import SchemaManager

class TestSchemaManager(unittest.TestCase):
    
    def setUp(self):
        """Initialisation de la base de données pour les tests"""
        self.db_path = ":memory:"  # Utilisation d'une BD en mémoire pour les tests
        self.manager = SchemaManager(self.db_path)
        self.manager.create_table("test_table", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

    def tearDown(self):
        """Fermeture de la connexion après chaque test"""
        self.manager.close_connection()

    def test_create_table(self):
        """Vérifie que la table est bien créée"""
        tables = self.manager.list_tables()
        self.assertIn("test_table", tables)

    def test_add_column(self):
        """Ajoute une colonne et vérifie qu'elle est bien ajoutée"""
        self.manager.add_column("test_table", "age", "INTEGER")
        schema = self.manager.validate_schema("test_table")
        column_names = [col[1] for col in schema]  # Récupérer les noms des colonnes
        self.assertIn("age", column_names)

    def test_rename_table(self):
        """Teste le renommage d'une table"""
        self.manager.rename_table("test_table", "renamed_table")
        tables = self.manager.list_tables()
        self.assertIn("renamed_table", tables)
        self.assertNotIn("test_table", tables)

    def test_rename_column(self):
        """Teste le renommage d'une colonne"""
        self.manager.rename_column("test_table", "name", "full_name")
        schema = self.manager.validate_schema("test_table")
        column_names = [col[1] for col in schema]
        self.assertIn("full_name", column_names)
        self.assertNotIn("name", column_names)

    def test_check_foreign_keys(self):
        """Vérifie si les clés étrangères sont activées après activation"""
        self.manager.enable_foreign_keys()
        self.assertTrue(self.manager.check_foreign_keys())

    def test_drop_table(self):
        """Teste la suppression d'une table"""
        self.manager.drop_table("test_table")
        tables = self.manager.list_tables()
        self.assertNotIn("test_table", tables)

if __name__ == '__main__':
    unittest.main()


# import unittest
# import os
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
# from src.modules.schema_manager import SchemaManager  

# class TestSchemaManager(unittest.TestCase):
#     def setUp(self):
#         """Initialisation avant chaque test : Création d'une base de données temporaire et d'une table de test."""
#         self.db_path = "test_database.sqlite"
#         self.manager = SchemaManager(self.db_path)
#         self.manager.create_table("test_table", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

#     def tearDown(self):
#         """Nettoyage après chaque test : Fermeture de la connexion et suppression du fichier de base de données."""
#         self.manager.close_connection()
#         os.remove(self.db_path)

#     def test_create_table(self):
#         """Vérifie que la table a bien été créée dans la base de données."""
#         tables = self.manager.list_tables()
#         self.assertIn("test_table", tables)

#     def test_rename_table(self):
#         """Vérifie que le renommage d'une table fonctionne correctement."""
#         self.manager.rename_table("test_table", "renamed_table")
#         tables = self.manager.list_tables()
#         self.assertIn("renamed_table", tables)
#         self.assertNotIn("test_table", tables)

#     def test_add_column(self):
#         """Teste l'ajout d'une nouvelle colonne à une table existante."""
#         self.manager.add_column("test_table", "email", "TEXT")
#         schema = [col[1] for col in self.manager.validate_schema("test_table")]
#         self.assertIn("email", schema)

#     def test_rename_column(self):
#         """Teste le renommage d'une colonne en s'assurant que l'ancienne n'existe plus et que la nouvelle est bien présente."""
#         self.manager.add_column("test_table", "email", "TEXT")
#         self.manager.rename_column("test_table", "email", "contact")
#         schema = [col[1] for col in self.manager.validate_schema("test_table")]
#         self.assertIn("contact", schema)
#         self.assertNotIn("email", schema)

#     def test_validate_schema(self):
#         """Vérifie que la structure de la table est correcte après sa création."""
#         schema = self.manager.validate_schema("test_table")
#         self.assertEqual(len(schema), 2)
#         self.assertEqual(schema[0][1], "id")
#         self.assertEqual(schema[1][1], "name")

#     def test_check_foreign_keys(self):
#         """Vérifie que les clés étrangères sont bien activées après activation explicite."""
#         self.manager.enable_foreign_keys()
#         self.assertTrue(self.manager.check_foreign_keys())

#     def test_drop_table(self):
#         """Teste la suppression d'une table et vérifie qu'elle n'existe plus dans la base de données."""
#         self.manager.drop_table("test_table")
#         tables = self.manager.list_tables()
#         self.assertNotIn("test_table", tables)

# if __name__ == "__main__":
#     unittest.main()
