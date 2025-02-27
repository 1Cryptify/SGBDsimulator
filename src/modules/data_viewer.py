import logging
import csv
from .crud_operator import CRUDOperator
from typing import List, Dict, Any

class DataViewer:
    def __init__(self, db_path: str):
        """Initialisation avec le chemin de la base de données SQLite"""
        self.crud_operator = CRUDOperator(db_path)

    def display_data(self, table_name: str, conditions: str = '', params: tuple = ()) -> None:
        """Affiche les données de la table spécifiée."""
        data = self.crud_operator.read(table_name, conditions, params)
        if data:
            for record in data:
                print(record)
        else:
            print(f"Aucun enregistrement trouvé dans la table {table_name}.")

    def export_data(self, table_name: str, file_path: str, conditions: str = '', params: tuple = ()) -> None:
        """Exporte les données de la table spécifiée vers un fichier CSV."""
        data = self.crud_operator.read(table_name, conditions, params)
        if data:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            logging.info(f"Données exportées avec succès vers {file_path}.")
        else:
            print(f"Aucun enregistrement à exporter depuis la table {table_name}.")

    def close(self) -> None:
        """Ferme la connexion à la base de données."""
        self.crud_operator.close()
