Para recibir las respuestas del cliente, se configura el webhook en Twilio:

### Pasos para Configurar el Webhook

**⚠️ IMPORTANTE**: La URL que se ve por defecto (`https://timberwolf-mastiff-9776.twil.io/demo-reply`) es de **Twilio Functions** (servicio serverless de Twilio), NO es nuestro servidor. Es necesario cambiarla por la URL de nuestro servidor, que en desarrollo nos la dará ngrox y en producción será la pertinente.

1. **Instalar y configurar ngrok** (solo para desarrollo local):
   
   **Instalación:**
   - Descarga ngrok desde: https://ngrok.com/download
   - O en Linux/WSL:
     ```bash
     wget https://bin.equinox.io/c/b/ykexe/ngrok-v3-stable-linux-amd64.tgz
     tar -xzf ngrok-v3-stable-linux-amd64.tgz
     ```
   
   **Configuración inicial (solo la primera vez):**
   - Crear una cuenta gratuita en https://ngrok.com/
   - Obtener el token de autenticación
   - Configurar el token:
     ```bash
     ngrok config add-authtoken TU_TOKEN_AQUI
     ```
   
   **Ejecutar ngrok:**
   ```bash
   ngrok http 8001
   ```
   
   **Copiar la URL:**
   - ngrok mostrará una URL HTTPS (ej: `https://abc123.ngrok.io`)
   - **Copiar esta URL completa** (se necesitará en el siguiente paso)
   - **Mantener ngrok corriendo** (no cerrar la terminal)

2. **En el panel de Twilio**:
   - Acceder a https://console.twilio.com/us1/develop/sms/sandbox
   - Buscar la sección **"When a message comes in"**
   - **Borrar** la URL por defecto (`https://timberwolf-mastiff-9776.twil.io/demo-reply`)
   - Configurar la URL: `https://tu-url-ngrok.ngrok.io/twilio/incoming`
   - Método: **POST**
   - Hacer clic en **"Save"**

3. **Verificar que ngrok está funcionando**:
   - La URL de ngrok debe estar activa (terminal de ngrok abierta)
   - Se puede probar: `curl https://tu-url-ngrok.ngrok.io/twilio/incoming` (debería dar error 405, pero significa que la URL es accesible)

4. **Verificar que funciona**:
   - Al responder "SI" o "NO" a un mensaje de WhatsApp
   - Se debe recibir una respuesta automática:
     - **SI** → Mensaje de confirmación y agradecimiento
     - **NO** → Mensaje preguntando por horas alternativas
   - Revisar los logs: `docker-compose logs backend | grep -i whatsapp`

5. **En producción**: Usar nuestro dominio real (e.g. test.ctic.es) en lugar de ngrok
