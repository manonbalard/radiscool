import sqlite3

conn = sqlite3.connect('recettes.db')
print("Connected successfully")

conn.execute('CREATE TABLE recettes (titre TEXT, ingrédients TEXT, étapes TEXT)')
print("Created table successfully!")

conn.close()