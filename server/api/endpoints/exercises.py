from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from ..db.database import get_db_connection

router = APIRouter()


class Exercise(BaseModel):
    title: str  # Novo campo: título do exercício
    lesson_id: int  # Novo campo: ID da aula associada ao exercício
    question: str
    options: Optional[List[str]] = None  # Lista de strings (ou None)
    answer: str
    type: str  # "multiple_choice" ou "coding"
    difficulty: str  # "easy", "medium", "hard"
    test_code: Optional[str] = None  # Código de teste para o exercício de tipo "coding"
    release_date: Optional[datetime] = None  # Data de liberação (pode ser None)

    
# Criar um exercício
@router.post("/exercicios")
def create_exercise(exercise: Exercise):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500 
        )
    cursor = conn.cursor()
    
    # converte múltipla escolha para JSON
    options_json = json.dumps(exercise.options) if exercise.options else None

    # converte a data para string
    release_date_str = exercise.release_date.strftime('%Y-%m-%d %H:%M:%S') if exercise.release_date else None
    
    # Insere o código de teste
    test_code_str = exercise.test_code if exercise.test_code else None

    cursor.execute(''' 
    INSERT INTO exercises (title, lesson_id, question, options, answer, type, difficulty, test_code, release_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) 
    ''', (exercise.title, exercise.lesson_id, exercise.question, options_json, exercise.answer, exercise.type, exercise.difficulty, test_code_str, release_date_str))
    
    conn.commit()
    conn.close()

    return JSONResponse(
        content={"mensagem": "Exercício criado com sucesso!"},
        status_code=201 
    )


# Listar todos os exercícios
@router.get("/exercicios")
def get_exercises():
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500 
        )
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM exercises')
    exercises = cursor.fetchall()
    if len(exercises) == 0:
        return JSONResponse(
            content={"mensagem": "Não existem exercícios em nosso banco de dados."},
            status_code=200
        )
    conn.close()
    
    return [
        {
            "id": ex[0],
            "title": ex[1],  # Incluindo o título
            "lesson_id": ex[2],  # Incluindo o lesson_id
            "question": ex[3],
            "options": json.loads(ex[4]) if ex[4] else None,
            "answer": ex[5],
            "type": ex[6],
            "difficulty": ex[7],
            "test_code": ex[8],  # Adicionando o test_code aqui
            "created_at": ex[9],
            "updated_at": ex[10],
            "release_date": ex[11]
        }
        for ex in exercises
    ]

# Buscar um dos exercícios
@router.get("/exercicios/{exercise_id}")
def get_exercise(exercise_id: int):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500 
        )

    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
    exercise = cursor.fetchone()

    conn.close()

    # Se não encontrar, retorna 404
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")

    return {
        "id": exercise[0],
        "title": exercise[1],  # Incluindo o título
        "lesson_id": exercise[2],  # Incluindo o lesson_id
        "question": exercise[3],
        "options": json.loads(exercise[4]) if exercise[4] else None,
        "answer": exercise[5],
        "type": exercise[6],
        "difficulty": exercise[7],
        "test_code": exercise[8],  # Adicionando o test_code aqui
        "created_at": exercise[9],
        "updated_at": exercise[10],
        "release_date": exercise[11]
    }


# Atualizar um exercício
@router.put("/exercicios/{exercise_id}")
def update_exercise(exercise_id: int, exercise: Exercise):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500 
        )
    cursor = conn.cursor()
    
    # converte múltipla escolha para JSON
    options_json = json.dumps(exercise.options) if exercise.options else None
    
    # converte a data para string
    release_date_str = exercise.release_date.strftime('%Y-%m-%d %H:%M:%S') if exercise.release_date else None
    
    # Insere o código de teste
    test_code_str = exercise.test_code if exercise.test_code else None

    cursor.execute('''
    UPDATE exercises
    SET title = ?, lesson_id = ?, question = ?, options = ?, answer = ?, type = ?, difficulty = ?, test_code = ?, release_date = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (exercise.title, exercise.lesson_id, exercise.question, options_json, exercise.answer, exercise.type, exercise.difficulty, test_code_str, release_date_str, exercise_id))

    conn.commit()
    conn.close()

    return JSONResponse(
        content={"mensagem": "Exercício alterado com sucesso!"},
        status_code=200
    )

# Deletar um exercício
@router.delete("/exercicios/{exercise_id}")
def delete_exercise(exercise_id: int):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
        content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
        status_code=500 
    )
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM exercises WHERE id = ?', (exercise_id,))
    
    conn.commit()
    conn.close()

    return JSONResponse(
        content={"mensagem": "Exercício removido com sucesso!"},
        status_code=200 
    )
