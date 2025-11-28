'''
Conexión a la DB
    Inicializa la conexión con PostgreSQL utilizando la URL de entorno y crea una sesión (SessionLocal) para las operaciones de lectura/escritura.
    Es importado por models.py y main.py para establecer la conexión física con la base de datos.
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()