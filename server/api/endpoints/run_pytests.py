from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db.database import get_db_connection
import subprocess
import tempfile
import pytest
import uuid
import os


router = APIRouter()

class CodeInput(BaseModel):
    code: str
    test_id: int

# Função para salvar o código do aluno em um arquivo temporário
def save_code_to_file(code: str, temp_dir: str):
    file_path = os.path.join(temp_dir, "student_code.py")
    with open(file_path, "w") as file:
        file.write(code)
    return file_path

# Função para rodar o pytest nos testes
def run_pytest(test_directory: str) -> str:
    result = subprocess.run(
            ["pytest", test_directory],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
    )
    # Processar a saída do pytest para um feedback mais amigável
    feedback = ""
    if result.returncode == 0:
        feedback = "Parabéns! Todos os testes passaram com sucesso!"
    else:
        feedback = "Alguns testes falharam. Veja os detalhes abaixo:\n"
        
        # Personalizar as falhas
        errors = result.stdout.splitlines()
        for line in errors:
            if line.startswith("E"):  # A linha de erro do pytest
                feedback += f"Erro: {line}\n"
            elif "AssertionError" in line:
                feedback += f"Falha: {line}\n"
            elif line.startswith("def "):  # Detalhes do teste falho
                feedback += f"Teste falhado: {line}\n"

    return feedback

# Endpoint para rodar os testes
@router.post("/run-tests")
async def run_tests_endpoint(input: CodeInput):
    code = input.code
    test_id = input.test_id
    
    # Conectar ao banco de dados SQLite
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar o código de teste no banco de dados
    cursor.execute("SELECT test_code FROM exercises WHERE id = ?", (test_id,))
    test_case = cursor.fetchone()
    conn.close()
    
    if not test_case:
        raise HTTPException(status_code=404, detail="Teste não encontrado.")
    
    # Criar um diretório temporário único para cada execução de teste
    temp_dir = tempfile.mkdtemp(prefix=f"test_{uuid.uuid4().hex}_")
    
    try:
        # Salvar o código do aluno em um arquivo temporário
        student_code_file = save_code_to_file(code, temp_dir)
        
        # Criar o arquivo de testes com pytest
        test_file_path = os.path.join(temp_dir, "test_student_code.py")
        with open(test_file_path, "w") as test_file:
            test_file.write(test_case[0])  # Escreve os testes do banco de dados no arquivo
        
        # Rodar o pytest para testar a função do aluno
        pytest_output = run_pytest(temp_dir)
    
    finally:
        # Limpeza do diretório temporário após execução
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
    
    # Retorna o feedback dos testes
    return {"test_feedback": pytest_output}