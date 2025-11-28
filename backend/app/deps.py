'''
Dependencias/Seguridad
    Contiene la función api_key_auth que valida que la API_KEY correcta esté presente en el encabezado de cada petición.
    Es inyectado en los endpoints de main.py (vía Depends()) para proteger la API.
'''

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

API_KEY = os.getenv("API_KEY")

# Configurar HTTPBearer para que Swagger muestre el botón de autorización
security = HTTPBearer()

def api_key_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Valida que el token Bearer sea igual a la API_KEY configurada.
    """
    token = credentials.credentials
    
    if token != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token