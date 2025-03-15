from fastapi import APIRouter, HTTPException
from ..db.database import get_db_connection
from fastapi.responses import JSONResponse
from bcrypt import hashpw, gensalt
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

#Modelo para Usuário
class User(BaseModel):
    name: str
    email: str
    password: str
    is_staff: bool
    last_login: datetime | None = None 

#Criar Usuário
@router.post("/usuarios")
def create_user(user: User):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500
        )
    cursor = conn.cursor()

    # verifica se não tem ninguém com o mesmo e-mail
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já está em uso.")

    # Hash da senha
    hashed_password = hashpw(user.password.encode('utf-8'), gensalt(rounds=12))

    # Mandando para o banco de dados
    cursor.execute('''
    INSERT INTO users (name, email, password, is_staff)
    VALUES (?, ?, ?, ?)
    ''', (user.name, user.email, hashed_password, user.is_staff))
    conn.commit()
    conn.close()

    return JSONResponse(
        content={"mensagem": "Usuário criado com sucesso!"},
        status_code=201
    )

# Listar todos os usuários
@router.get("/usuarios")
def get_users():
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500
        )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    if len(users) == 0:
        return JSONResponse(
            content={"mensagem": "Não existem usuários no banco de dados."},
            status_code=200
        )

    conn.close()

    return [
        {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "is_staff": user[4],
            "created_at": user[5],
            "updated_at": user[6],
            "last_login": user[7]
        }
        for user in users
    ]


# Buscar um usuário específico
@router.get("/usuarios/{user_id}")
def get_user(user_id: int):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500
        )

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    conn.close()

    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return {
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "is_staff": user[4],
        "created_at": user[5],
        "updated_at": user[6],
        "last_login": user[7]
    }


# Atualizar um usuário
@router.put("/usuarios/{user_id}")
def update_user(user_id: int, user: User):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500
        )
    cursor = conn.cursor()

    # verifica se já alguém com esse e-mail
    cursor.execute("SELECT * FROM users WHERE email = ? AND id != ?", (user.email, user_id))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já está em uso.")

    # Hash da senha
    hashed_password = hashpw(user.password.encode('utf-8'), gensalt(rounds=12))

    cursor.execute('''
    UPDATE users
    SET name = ?, email = ?, password = ?, is_staff = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (user.name, user.email, hashed_password, user.is_staff, user_id))

    conn.commit()
    conn.close()

    return JSONResponse(
        content={"mensagem": "Usuário atualizado com sucesso!"},
        status_code=200
    )


# Deletar um usuário
@router.delete("/usuarios/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500
        )
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()

    return JSONResponse(
        content={"mensagem": "Usuário removido com sucesso!"},
        status_code=200
    )