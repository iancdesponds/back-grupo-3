# API - FastAPI  **Desenvolvido para o projeto INFORMAR GAS**

## Como Rodar a API
1. Instale as dependências:
   ```sh
   pip install fastapi uvicorn
   ```
2. Execute o servidor:
   ```sh
   uvicorn main:app --reload
   ```
3. Acesse a documentação interativa:
   - [Swagger UI](http://127.0.0.1:8000/docs)
   - [Redoc](http://127.0.0.1:8000/redoc)

## Observações
- O banco de dados **SQLite** será criado automaticamente na primeira execução.
- Os exercícios de **múltipla escolha** armazenam as opções em formato JSON.


## Endpoints

### 1. Criar um Exercício
```http
POST /exercicios
```
#### Corpo da Requisição (JSON):
```json
{
    "question": "Qual a saída mostrada no terminal para: print(2 + 2)?",
    "options": ["2", "3", "4", "5"],
    "answer": "4",
    "type": "multiple_choice",
    "difficulty": "easy"
}
```
####  Resposta:
```json
{
    "mensagem": "Exercício criado com sucesso!"
}
```
---

### 2. Listar Todos os Exercícios
```http
GET /exercicios
```
#### Resposta:
```json
[
    {
        "id": 1,
        "question": "Qual a saída mostrada no terminal para: print(2 + 2)?",
        "options": ["2", "3", "4", "5"],
        "answer": "4",
        "type": "multiple_choice",
        "difficulty": "easy"
    }
]
```
---

### 3. Buscar um Exercício por ID
```http
GET /exercicios/{exercise_id}
```
#### Resposta:
```json
{
    "id": 1,
    "question": "Qual a saída mostrada no terminal para: print(2 + 2)?",
    "options": ["2", "3", "4", "5"],
    "answer": "4",
    "type": "multiple_choice",
    "difficulty": "easy"
}
```

### 4. Atualizar um Exercício
```http
PUT /exercicios/{exercise_id}
```
#### Corpo da Requisição (JSON):
```json
{
    "question": "Quanto é 3 + 3?",
    "options": ["5", "6", "7", "8"],
    "answer": "6",
    "type": "multiple_choice",
    "difficulty": "easy"
}
```
#### Resposta:
```json
{
    "mensagem": "Exercício atualizado com sucesso!"
}
```
---

### 5. Deletar um Exercício
```http
DELETE /exercicios/{exercise_id}
```
#### 📤 Resposta:
```json
{
    "mensagem": "Exercício deletado com sucesso!"
}
```