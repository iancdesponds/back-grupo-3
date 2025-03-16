from fastapi import APIRouter
from pydantic import BaseModel
import tempfile
import os
import subprocess

router = APIRouter()

# Definindo o modelo de entrada para o código do aluno
class CodeInput(BaseModel):
    code: str

# Função para salvar o código em um arquivo temporário
def save_code_to_tempfile(code: str, temp_dir: str) -> str:
    file_path = os.path.join(temp_dir, "student_code.py")
    with open(file_path, "w") as file:
        file.write(code)
    return file_path

# Função para rodar o código do aluno
def run_student_code(file_path: str):
    result = subprocess.run(
        ['python', file_path], 
        capture_output=True, 
        text=True
    )
    return result.stdout, result.stderr

# Endpoint para rodar o código do aluno
@router.post("/run-code")
async def submit_code(input: CodeInput):
    code = input.code
    
    # Criar um diretório temporário único para a execução do código
    temp_dir = tempfile.mkdtemp(prefix="student_code_")

    try:
        # Salvar o código do aluno no arquivo temporário
        student_code_file = save_code_to_tempfile(code, temp_dir)

        # Executar o código do aluno
        output, error = run_student_code(student_code_file)

        return {"output": output, "error": error}

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Limpeza do diretório temporário após execução
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))