from fastapi import APIRouter
from pydantic import BaseModel
import subprocess
import pytest

router = APIRouter()

class CodeInput(BaseModel):
    code: str

# Função para salvar o código do aluno em um arquivo Python
def save_code_to_file(code: str):
    with open("workspace/student_code/student_code.py", "w") as file:
        file.write(code)

# Função para rodar o pytest nos testes
# Função para rodar o pytest nos testes e personalizar o feedback
def run_pytest():
    result = subprocess.run(['pytest', '--maxfail=5', '--disable-warnings', '--capture=no'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
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

@router.post("/run-tests")
async def run_tests_endpoint(input: CodeInput):
    code = input.code
    
    # Salvar o código do aluno em um arquivo temporário
    save_code_to_file(code)

    
    # Criar o arquivo de testes com pytest
    test_code = """
from student_code import soma

def test_soma():
    assert soma(5, 10) == 15
    assert soma(3, 7) == 10
"""
    with open("workspace/student_code/test_student_code.py", "w") as test_file:
        test_file.write(test_code)

    # Rodar o pytest para testar a função do aluno
    pytest_output = run_pytest()
    
    # Retorna tanto a saída do programa quanto o feedback personalizado dos testes
    return {"test_feedback": pytest_output}