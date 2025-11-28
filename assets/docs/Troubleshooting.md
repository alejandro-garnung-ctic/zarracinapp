### El WhatsApp no se envía
- **Verificar Twilio Sandbox**: El número debe estar registrado en el Sandbox
  - Acceder a https://console.twilio.com/us1/develop/sms/sandbox
  - Enviar el código de join al número de Twilio desde WhatsApp
- Verificar que las credenciales de Twilio están correctas en `.env`
- Verificar que `DISABLE_WHATSAPP=false` en `.env`
- Verificar que el número del cliente está en formato internacional (+34...)
- Usar el endpoint de prueba: `POST /test/whatsapp?phone=TU_NUMERO`
- Revisar los logs del contenedor: `docker-compose logs backend | grep -i whatsapp`

### El webhook no recibe respuestas
- Verificar que ngrok está corriendo
- Verificar que la URL del webhook en Twilio es correcta
- Revisar los logs: `docker-compose logs backend`

### El dashboard no carga
- Verificar que el backend está corriendo en el puerto 8001
- Verificar que el archivo `backend/app/static/dashboard.html` existe
- Revisar la consola del navegador para errores de JavaScript
- Verificar que la API_KEY en el dashboard coincide con la del `docker-compose.yml`

### Los estados no se actualizan en el dashboard
- Verificar que el webhook de Twilio está configurado correctamente
- Verificar que las respuestas del cliente están llegando al servidor
- Revisar los logs del backend: `docker-compose logs backend`
- Verificar que el dashboard se está actualizando (cada 5 segundos)