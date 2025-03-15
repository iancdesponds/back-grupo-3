from fastapi import APIRouter
from pydantic import BaseModel
import os
import subprocess

router = APIRouter()

class CodeInput(BaseModel):
    code: str


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