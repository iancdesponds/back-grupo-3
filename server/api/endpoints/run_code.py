from fastapi import APIRouter
from pydantic import BaseModel
import subprocess
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
from ..db.database import get_db_connection
from .google_drive import save_code_to_drive
import io
import google.auth
import time


router = APIRouter()

class CodeInput(BaseModel):
    code: str

class SaveCodeRequest(BaseModel):
    user_email: str
    code: str
    exercise_name: str

class CodeExecutionRequest(BaseModel):
    user_email: str
    student_code: str
    notebook_id: str


# Função para obter o ID da pasta do aluno
def get_student_folder_id(user_email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT drive_folder_id FROM users WHERE email = ?", (user_email,))
    result = cursor.fetchone()
    
    conn.close()
    
    if not result:
        return None
    return result[0]

# Função para rodar o código do aluno no notebook

@router.post("/save-code")
def save_code(request: SaveCodeRequest):
    try:
        file_id = save_code_to_drive(request.user_email, request.code, request.exercise_name)
        return JSONResponse(content={"message": "Código salvo com sucesso!", "file_id": file_id}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.post("/run-code")
async def submit_code(input: CodeInput):
    code = input.code
    
    # Aqui você pode rodar o código enviado com segurança (usando subprocess)
    try:
        # Salvar o código em um arquivo temporário e executá-lo
        with open("workspace/student_code/student_code.py", "w") as file:
            file.write(code)

        result = subprocess.run(['python', 'workspace/student_code/student_code.py'], capture_output=True, text=True)
        output = result.stdout
        error = result.stderr

        return {"output": output, "error": error}

    except Exception as e:
        return {"error": str(e)}