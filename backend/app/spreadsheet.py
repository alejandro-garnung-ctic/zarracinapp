'''
Utilidades para leer Google Sheets
'''

import gspread
from google.oauth2.service_account import Credentials
import os
import json

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_google_credentials():
    """Crea las credenciales de Google desde variables de entorno"""
    creds_dict = {
        "type": os.getenv("GOOGLE_SERVICE_ACCOUNT_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
    }
    return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)


def get_spreadsheet_client():
    """Obtiene el cliente de Google Sheets"""
    creds = get_google_credentials()
    return gspread.authorize(creds)


def read_spreadsheet():
    """Lee el spreadsheet configurado y devuelve los datos"""
    try:
        client = get_spreadsheet_client()
        sheet_url = os.getenv("GOOGLE_SHEETS_URL")
        sheet = client.open_by_url(sheet_url).sheet1
        rows = sheet.get_all_records()
        return rows
    except Exception as e:
        raise Exception(f"Error leyendo spreadsheet: {str(e)}")

