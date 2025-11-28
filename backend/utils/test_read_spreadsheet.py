import gspread
from google.oauth2.service_account import Credentials

# Rutas y scopes
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
import os
# Ruta: desde /app/utils/ a /app/assets/
script_dir = os.path.dirname(os.path.abspath(__file__))
creds_path = os.path.join(os.path.dirname(script_dir), "assets", "asdih-zarracina-5a9be1772123.json")
creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)

# Conectar
client = gspread.authorize(creds)

# Abrir la hoja por URL
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1LAU4MwLTa7LB8XQGGczv5m0InYfcskC1HAc3IT8_5Eg/edit?gid=0#gid=0").sheet1

# Leer datos
rows = sheet.get_all_records()
print(rows)
