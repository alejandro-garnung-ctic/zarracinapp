
## Autenticación

Todas las peticiones (excepto el webhook de Twilio) requieren:

```
Authorization: Bearer supersecreta123
```

**Usando Swagger UI** (recomendado para pruebas):
1. Abrir http://localhost:8001/docs
2. Hacer clic en el botón **"Authorize"** (🔒) en la parte superior derecha
3. Introducir el token: `supersecreta123` (sin "Bearer")
4. Hacer clic en "Authorize" y luego "Close"
5. Ahora se pueden probar todos los endpoints directamente desde la interfaz

## Listado de endpoints

### Endpoints de Clientes

#### Crear un Cliente

```bash
curl -X POST http://localhost:8001/customers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer supersecreta123" \
  -d '{
    "name": "Bar Manolo",
    "phone": "+34612345678",
    "delivery_hours_open": "10:00:00",
    "delivery_hours_close": "22:00:00",
    "timezone": "Europe/Madrid"
  }'
```

#### Listar Todos los Clientes

```bash
curl -X GET http://localhost:8001/customers \
  -H "Authorization: Bearer supersecreta123"
```

#### Obtener un Cliente por ID

```bash
curl -X GET http://localhost:8001/customers/{customer_id} \
  -H "Authorization: Bearer supersecreta123"
```

#### Actualizar un Cliente

```bash
curl -X PUT http://localhost:8001/customers/{customer_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer supersecreta123" \
  -d '{
    "name": "Bar Manolo Actualizado",
    "phone": "+34687654321",
    "delivery_hours_open": "09:00:00",
    "delivery_hours_close": "23:00:00"
  }'
```

**Nota**: Solo se necesitan incluir los campos que se desean actualizar. Los demás se mantienen igual.

#### Eliminar un Cliente

```bash
curl -X DELETE http://localhost:8001/customers/{customer_id} \
  -H "Authorization: Bearer supersecreta123"
```

### Endpoints de Envíos

#### Crear un Envío (dispara WhatsApp automáticamente)

```bash
curl -X POST http://localhost:8001/shipments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer supersecreta123" \
  -d '{
    "customer_id": "UUID_DEL_CLIENTE",
    "description": "Palé de refrescos",
    "planned_delivery_time": "2025-11-25T14:30:00"
  }'
```

**Nota**: Si el cliente tiene un teléfono válido y `DISABLE_WHATSAPP` está en `"false"`, se enviará automáticamente un WhatsApp.

#### Listar Todos los Envíos

```bash
curl -X GET http://localhost:8001/shipments \
  -H "Authorization: Bearer supersecreta123"
```

#### Listar Envíos de un Cliente Específico

```bash
curl -X GET "http://localhost:8001/shipments?customer_id={customer_id}" \
  -H "Authorization: Bearer supersecreta123"
```

#### Obtener un Envío por ID

```bash
curl -X GET http://localhost:8001/shipments/{shipment_id} \
  -H "Authorization: Bearer supersecreta123"
```

#### Obtener Interacciones de un Envío

```bash
curl -X GET http://localhost:8001/shipments/{shipment_id}/interactions \
  -H "Authorization: Bearer supersecreta123"
```

**Nota**: Las interacciones incluyen todos los mensajes enviados y recibidos relacionados con ese envío (WhatsApp outbound/inbound).

### Leer Google Spreadsheet

```bash
curl -X GET http://localhost:8001/spreadsheet \
  -H "Authorization: Bearer supersecreta123"
```

**Nota**: Lee el Google Spreadsheet configurado en `GOOGLE_SHEETS_URL` y devuelve todos los registros. Requiere que las credenciales de Google estén correctamente configuradas en el `.env`.

### Procesar Spreadsheet y Crear Shipments

```bash
curl -X POST http://localhost:8001/spreadsheet/process \
  -H "Authorization: Bearer supersecreta123"
```

**Nota**: Lee el spreadsheet, crea clientes y shipments automáticamente, y envía WhatsApp si está habilitado. Solo crea registros si no existen ya (evita duplicados).

### Probar Envío de WhatsApp (Endpoint de Prueba)

```bash
curl -X POST "http://localhost:8001/test/whatsapp?phone=34612345678" \
  -H "Authorization: Bearer supersecreta123"
```

**Nota**: Endpoint útil para verificar que Twilio Sandbox está configurado correctamente. Se reemplaza el número de teléfono con el número deseado (con o sin el prefijo `+`).