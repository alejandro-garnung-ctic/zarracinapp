
## 🗂️ Estructura del Proyecto

```
zarracinapp/
├── backend/
│   ├── app/
│   │   ├── main.py          # Endpoints de la API
│   │   ├── models.py         # Modelos de la base de datos
│   │   ├── schemas.py        # Esquemas Pydantic
│   │   ├── database.py       # Configuración de DB
│   │   ├── deps.py           # Dependencias (autenticación)
│   │   └── static/
│   │       └── dashboard.html # Frontend simple del dashboard
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   ├── Dockerfile            # Dockerfile personalizado para PostgreSQL
│   └── init.sql              # Script de inicialización de DB
├── docker-compose.yml
└── README.md
```

**Nota (para DESARROLLADORES)**: El `init.sql` se copia automáticamente en la imagen de PostgreSQL durante el build (a través de `db/Dockerfile`), evitando problemas de montaje de volúmenes en WSL2.
  
## 🏗️ Arquitectura

- **Backend**: FastAPI (Python)
- **Base de Datos**: PostgreSQL
- **Mensajería**: Twilio (WhatsApp API)
- **Frontend**: Dashboard HTML simple
- **Contenedores**: Docker Compose

## 🔐 Seguridad

- **API_KEY**: Protege los endpoints de la API
- **Webhook de Twilio**: No requiere API_KEY (Twilio valida con su propia firma)
- **DISABLE_WHATSAPP**: Variable de entorno para deshabilitar rápidamente todos los envíos de WhatsApp (útil para pruebas o emergencias)
- **En producción**: Cambiar todas las claves por valores seguros
