from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from bcrypt import hashpw, gensalt, checkpw
import jwt
from .google_drive import create_student_folder
from datetime import datetime, timedelta
from pydantic import BaseModel
from ..db.database import get_db_connection

# Modelo para usuário
class User(BaseModel):
    name: str
    email: str
    password: str
    is_staff: bool
    last_login: datetime | None = None

router = APIRouter()

SECRET_KEY = "secret"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Modelo de entrada para Login
class UserLogin(BaseModel):
    email: str
    password: str

# Função para gerar o token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Função para obter o usuário do token JWT
def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise credentials_exception

class User(BaseModel):
    name: str
    email: str
    password: str
    is_staff: bool
    last_login: datetime | None = None 

@router.post("/register")
def create_user(user: User):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500
        )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já está em uso.")

    hashed_password = hashpw(user.password.encode('utf-8'), gensalt(rounds=12))

    # Criar a pasta do usuário no Google Drive
    user_folder_id = create_student_folder(user.name)

    cursor.execute('''
    INSERT INTO users (name, email, password, is_staff, drive_folder_id)
    VALUES (?, ?, ?, ?, ?)
    ''', (user.name, user.email, hashed_password, user.is_staff, user_folder_id))
    
    conn.commit()
    conn.close()

    return JSONResponse(
        content={"mensagem": "Usuário criado com sucesso!", "drive_folder_id": user_folder_id},
        status_code=201
    )
# Login de usuário e geração do token
@router.post("/login")
def login(user: UserLogin):
    conn = get_db_connection()
    if not conn:
        return JSONResponse(
            content={"mensagem": "Não foi possível estabelecer a conexão com o banco de dados."},
            status_code=500
        )
    cursor = conn.cursor()

    # Verificar se o usuário existe
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()

    if db_user is None:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")
    
    # Verificar a senha
    if not checkpw(user.password.encode('utf-8'), db_user[3]):
        raise HTTPException(status_code=400, detail="E-mail ou Senha incorreta.")

    # Gerar o token JWT
    access_token = create_access_token({"sub": db_user[2]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    return {"access_token": access_token, "token_type": "bearer"}