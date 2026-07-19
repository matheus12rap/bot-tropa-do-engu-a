import sqlite3

conexao = sqlite3.connect("dados.db")

cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jogadores(
    id INTEGER PRIMARY KEY,
    nome TEXT,
    tempo INTEGER DEFAULT 0
)
""")

conexao.commit()
