from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from ..db.database import get_db_connection

router = APIRouter()


class Exercise(BaseModel):
    question: str
    options: Optional[List[str]] = None  # Lista de strings (ou None)
    answer: str
    type: str  # "multiple_choice" ou "coding"
    difficulty: str  # "easy", "medium", "hard"
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
    
    # converte multipla escolha um json
    options_json = json.dumps(exercise.options) if exercise.options else None

    # converte a data para string
    release_date_str = exercise.release_date.strftime('%Y-%m-%d %H:%M:%S') if exercise.release_date else None
    
    cursor.execute(''' 
    INSERT INTO exercises (question, options, answer, type, difficulty, release_date)
    VALUES (?, ?, ?, ?, ?, ?) 
    ''', (exercise.question, options_json, exercise.answer, exercise.type, exercise.difficulty, release_date_str))
    
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
            "question": ex[1],
            "options": json.loads(ex[2]) if ex[2] else None,
            "answer": ex[3],
            "type": ex[4],
            "difficulty": ex[5],
            "created_at": ex[6],
            "updated_at": ex[7],
            "release_date": ex[8]
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
        "question": exercise[1],
        "options": json.loads(exercise[2]) if exercise[2] else None,
        "answer": exercise[3],
        "type": exercise[4],
        "difficulty": exercise[5],
        "created_at": exercise[6],
        "updated_at": exercise[7],
        "release_date": exercise[8]
    }

# Atualizar um exercício
@router.put("/exercicios")
def update_exercise(exercise_id: int, exercise: Exercise):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
        content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
        status_code=500 
    )
    cursor = conn.cursor()
    
    # converte multipla escolha para string
    options_json = json.dumps(exercise.options) if exercise.options else None
    
    # converte a data para string
    release_date_str = exercise.release_date.strftime('%Y-%m-%d %H:%M:%S') if exercise.release_date else None

    cursor.execute('''
    UPDATE exercises
    SET question = ?, options = ?, answer = ?, type = ?, difficulty = ?, release_date = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (exercise.question, options_json, exercise.answer, exercise.type, exercise.difficulty, release_date_str, exercise_id))

    conn.commit()
    conn.close()

    return JSONResponse(
        content={"mensagem": "Exercício alterado com sucesso!"},
        status_code=200
    )

# Deletar um exercício
@router.delete("/exercicios/{exercise_id}")
def delete_exercise(exercise_id:int):
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
