import sqlite3

# Connexion à la base de données (création si elle n'existe pas)
def get_db_connection():
    conn = sqlite3.connect('items.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialiser la base de données et créer une table
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Créer un nouvel élément
def create_item(name):
    conn = get_db_connection()
    conn.execute('INSERT INTO items (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

# Lire tous les éléments
def read_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return items

# Mettre à jour un élément
def update_item(item_id, new_name):
    conn = get_db_connection()
    conn.execute('UPDATE items SET name = ? WHERE id = ?', (new_name, item_id))
    conn.commit()
    conn.close()

# Supprimer un élément
def delete_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

# Fonction principale pour tester le CRUD
def main():
    init_db()  # Initialiser la base de données

    # Création d'éléments
    print("Création d'éléments...")
    create_item("Item 1")
    create_item("Item 2")
    print("Éléments après création : ", read_items())

    # Mise à jour d'un élément
    print("Mise à jour de l'élément 1...")
    update_item(1, "Item 1 Updated")
    print("Éléments après mise à jour : ", read_items())

    # Suppression d'un élément
    print("Suppression de l'élément 2...")
    delete_item(2)
    print("Éléments après suppression : ", read_items())

if __name__ == "__main__":
    main()