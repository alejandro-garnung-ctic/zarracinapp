### Características

- **Lista de Envíos**: 
  - Muestra todos los envíos con su estado actualizado
  - Estados con colores:
    - 🟡 **Pendiente** (pending): Envío creado, esperando respuesta del cliente
    - 🟢 **Confirmado** (confirmed): Cliente respondió "SI"
    - 🔴 **Rechazado** (rejected): Cliente respondió "NO"
  - Muestra: Cliente, Descripción, Fecha y hora previstas, Estado y Fecha de creación

- **Lista de Clientes**:
  - Todos los clientes registrados en el sistema
  - Muestra: Nombre, Teléfono y Horario de entrega

- **Actualización Automática**:
  - El dashboard se refresca automáticamente cada **5 segundos**
  - No se necesita recargar la página manualmente
  - Los cambios de estado se reflejan en tiempo real

### Uso del Dashboard

1. **Acceder**: Abrir `http://localhost:8001/dashboard` en el navegador
2. **Monitorear**: Observar cómo cambian los estados cuando los clientes responden
3. **Verificar**: Confirmar que los envíos se crean correctamente y los estados se actualizan

### Nota sobre la API_KEY (para DESARROLLADORES)

El dashboard tiene la API_KEY hardcodeada en el código JavaScript (`supersecreta123` por defecto). Si se cambia la `API_KEY` en `docker-compose.yml`, también se debe actualizar en el archivo `backend/app/static/dashboard.html` (línea con `const API_KEY = 'supersecreta123';`).
