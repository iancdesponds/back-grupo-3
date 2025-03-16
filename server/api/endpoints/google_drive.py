from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from fastapi import APIRouter, HTTPException, Depends
from googleapiclient.http import MediaIoBaseUpload
from ..db.database import get_db_connection
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
import nbformat
import subprocess
import io
import json


# Caminho para o JSON da conta de serviço
SERVICE_ACCOUNT_FILE = "cred/informarinsper-8c2aa50a7953.json"


# Autenticação no Google Drive
def get_drive_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=creds)

# Criar uma pasta no Google Drive
def create_student_folder(user_name):
    service = get_drive_service()
    
    folder_metadata = {
        "name": user_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": ["1FZmCiTeULH7f9cL9nVkRH-Mn9zjHV4io"]  # Substituir pelo ID da pasta principal do projeto
    }

    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder.get("id")

import io
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

def download_file_from_drive(file_id, file_path):
    drive_service = get_drive_service()

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    print(f"Arquivo {file_path} baixado com sucesso!")

# Função para criar pasta do exercício se não existir
def create_exercise_folder(service, parent_folder_id, exercise_name):
    # Verifica se a pasta já existe
    results = service.files().list(
        q=f"'{parent_folder_id}' in parents and name = '{exercise_name}' and mimeType = 'application/vnd.google-apps.folder'",
        spaces='drive',
        fields="files(id, name)"
    ).execute()
    
    # Se a pasta não existir, cria a pasta
    if not results.get('files', []):
        folder_metadata = {
            'name': exercise_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder['id']
    
    # Caso a pasta já exista, retorna o ID da pasta
    return results['files'][0]['id']

# Função para salvar o código no Google Drive
def save_code_to_drive(user_email: str, code: str, exercise_name: str):
    drive_service = get_drive_service()
    
    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT drive_folder_id FROM users WHERE email = ?", (user_email,))
    result = cursor.fetchone()

    conn.close()

    # Cria uma pasta para o exercício, se ela não existir
    folder_id = create_exercise_folder(drive_service, result[0],  exercise_name)

    with open('student_code.py', 'w') as f:
        f.write(code)

    # Cria o arquivo de código do aluno dentro da pasta do exercício
    file_metadata = {
        'name': f"{exercise_name}.py",  # Nome do arquivo
        'parents': [folder_id]  # Coloca o arquivo dentro da pasta do exercício
    }
    media = MediaFileUpload('student_code.py', mimetype='application/python')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file['id']
