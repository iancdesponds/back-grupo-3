from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from server.api.db.database import get_db_connection

router = APIRouter()

# Modelo para representar a resposta de aula
class Lesson(BaseModel):
    id: int
    title: str
    description: str

# Modelo para receber dados de uma nova aula
class LessonCreate(BaseModel):
    title: str
    description: str

# Rota para obter todas as aulas
@router.get("/lessons", response_model=List[Lesson])
async def get_lessons():
    conn = get_db_connection()

    if not conn:
        HTTPException(status_code=500, detail='Não foi possível estabelecer conexão com o banco de dados.')

    cursor = conn.cursor()
    try:
        # Consulta SQL para pegar as aulas
        query = "SELECT id, title, description FROM lessons"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Retorna os resultados como uma lista de objetos Lesson
        lessons = [Lesson(id=row[0], title=row[1], description=row[2]) for row in rows]
        return lessons

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco: {str(e)}")
    finally:
        conn.close()

# Rota para criar uma nova aula
@router.post("/lessons", response_model=Lesson)
async def create_lesson(lesson: LessonCreate):
    conn = get_db_connection()

    if not conn:
        HTTPException(status_code=500, detail='Não foi possível estabelecer conexão com o banco de dados.')

    cursor = conn.cursor()
    try:
        # Consulta SQL para inserir uma nova aula
        query = """
        INSERT INTO lessons (title, description)
        VALUES (?, ?)
        """
        # Executa a consulta SQL de inserção
        cursor.execute(query, (lesson.title, lesson.description))
            # Commit para garantir que a alteração seja salva
        conn.commit()

        # Recupera o id da nova aula inserida
        new_lesson_id = cursor.lastrowid

        # Retorna a aula criada com o id gerado
        return Lesson(id=new_lesson_id, title=lesson.title, description=lesson.description)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar a aula: {str(e)}")
    finally:
        conn.close()