import sqlite3

# Conectar ao banco de dados SQLite (cria o arquivo se não existir)
conn = sqlite3.connect('db_exercises.db')
cursor = conn.cursor()

# Criar a tabela 'exercises'
cursor.execute('''
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    options TEXT,  -- Armazena as opções em formato JSON (caso haja)
    answer TEXT NOT NULL,
    type TEXT NOT NULL,  -- "multiple_choice" ou "coding"
    difficulty TEXT NOT NULL  -- "easy", "medium", "hard"
)
''')

# Confirmar e fechar
conn.commit()
conn.close()

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('db_exercises.db')
    return conn