import sqlite3

# Conectar ao banco de dados SQLite (cria o arquivo se não existir)
conn = sqlite3.connect('db_project.db')
cursor = conn.cursor()

# cria a tabela 'exercises'
cursor.execute('''
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    release_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    lesson_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    options TEXT,  -- Armazena as opções em formato JSON (caso haja)
    answer TEXT DEFAULT NULL,
    type TEXT NOT NULL,  -- "multiple_choice" ou "coding"
    difficulty TEXT NOT NULL, 
    test_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    release_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);
''')

# cria a tabela 'users'
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  
    is_staff INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# criar a tabela 'performance'
cursor.execute('''
CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,  
    exercise_id INTEGER NOT NULL,  
    score INTEGER, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);
''')

# Confirmar e fechar
conn.commit()
conn.close()

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('db_project.db')
    return conn