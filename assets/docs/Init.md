## 🚀 Pasos para Iniciar

Para levantar el sistema, incluyendo base de datos, aplicación principal, API y dashboard, sigue los siguientes pasos:

Antes de nada, clonar el proyecto:

```bash
git clone https://github.com/alejandro-garnung-ctic/zarracinapp.git && git checkout origin main && git pull
```

### 1. Configurar Variables de Entorno

**Importante**: Copiar `.env.example` a `.env` y configurar las variables de entorno pertinentes:

```bash
cp .env.example .env
```

Luego se edita `.env` con las credenciales reales. El archivo `.env` (contacta con el dueño del repo para acceder a este) no se sube a git por seguridad.

**Variables principales a configurar:**

- `API_KEY`: Clave secreta para autenticar las peticiones a la API
- `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN`: Credenciales de Twilio
- `TWILIO_WHATSAPP_FROM`: Número de WhatsApp (sandbox para pruebas)
- `GOOGLE_SHEETS_URL`: URL del Google Spreadsheet
- `GOOGLE_*`: Credenciales de Google Service Account (del JSON)

Ver `.env.example` para ver todas las variables disponibles.

### 2. Levantar los Servicios

```bash
docker compose down && docker compose build --no-cache && docker compose up -d
```

Esto iniciará:
- **PostgreSQL** en el puerto local `5400`
- **Backend FastAPI** en `http://localhost:8050`
- **Dashboard web** en `http://localhost:8050/dashboard`
- **Adminer** (gestor de BD) en `http://localhost:8100`

Finalmente, crea la URL pública segura mediante Ngrok. Ver [Ngrok.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/Ngrok.md).
