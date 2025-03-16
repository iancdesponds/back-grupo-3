from fastapi import APIRouter
from pydantic import BaseModel
from .google_drive import download_file_from_drive
from ..db.database import get_db_connection
import subprocess
import time
import pytest
import uuid
import os
import shutil

router = APIRouter()

class CodeInput(BaseModel):
    exercise_name: str
    code: str  # Código enviado pelo aluno

# Função para salvar o código do aluno em um arquivo Python
def save_code_to_file(code: str):
    with open("workspace/student_code/student_code.py", "w") as file:
        file.write(code)

# Função para rodar pytest
def run_pytest(test_dir):
    result = subprocess.run(
        ['pytest', '--maxfail=5', '--disable-warnings', '--capture=no'],
        cwd=test_dir,  # Rodar os testes dentro da pasta isolada do aluno
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    feedback = "Parabéns! Todos os testes passaram com sucesso!" if result.returncode == 0 else "Alguns testes falharam. Veja os detalhes abaixo:\n"
    errors = result.stdout.splitlines()

    for line in errors:
        if line.startswith("E"):
            feedback += f"Erro: {line}\n"
        elif "AssertionError" in line:
            feedback += f"Falha: {line}\n"
        elif line.startswith("def "):
            feedback += f"Teste falhado: {line}\n"

    return feedback

def get_test_file_id(exercise_name: str):
    """
    Busca o ID do arquivo de testes do Google Drive no banco de dados.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT drive_file_id FROM exercises WHERE name = ?", (exercise_name,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None

@router.post("/run-tests")
async def run_tests_endpoint(input: CodeInput):
    """
    Salva o código do aluno em um diretório isolado, baixa os testes do Google Drive e executa os testes.
    """
    # Criar um ID único para esse teste (evita conflitos entre alunos)
    test_id = str(uuid.uuid4())
    temp_dir = f"workspace/tests/{test_id}"
    os.makedirs(temp_dir, exist_ok=True)

    # Salvar código do aluno no diretório temporário
    student_code_path = os.path.join(temp_dir, "student_code.py")
    with open(student_code_path, "w") as file:
        file.write(input.code)

    # Buscar o ID do arquivo de teste no Google Drive (do banco de dados)
    test_code_id = '1AK0P85puZ7kQ7l-uo-W0000ld9BRY31r'
    if not test_code_id:
        return {"error": "Arquivo de teste não encontrado no Drive"}

    # Baixar código de testes no diretório temporário
    test_code_path = os.path.join(temp_dir, "test_student_code.py")
    download_file_from_drive(test_code_id, test_code_path)

    # Executar pytest
    pytest_output = run_pytest(temp_dir)

    time.sleep(2)

    # Remover diretório temporário após a execução
    shutil.rmtree(temp_dir)

    # Retorna o feedback dos testes
    return {"test_feedback": pytest_output}