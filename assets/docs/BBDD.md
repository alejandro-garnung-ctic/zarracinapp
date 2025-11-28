## 🗄️ Adminer - Gestor de Base de Datos

Adminer es una herramienta web simple para gestionar la base de datos PostgreSQL desde el navegador.

### Acceso

1. Abrir **http://localhost:8081** en el navegador
2. Completar el formulario de conexión:
   - **Sistema**: PostgreSQL
   - **Servidor**: `db` (nombre del contenedor)
   - **Usuario**: `poc_user`
   - **Contraseña**: `poc_password`
   - **Base de datos**: `poc_db`
3. Hacer clic en **Entrar**

### Funcionalidades

- Ver todas las tablas (`customer`, `shipment`, `delivery_interaction`)
- Consultar datos con SQL
- Insertar, editar y eliminar registros
- Ver estructura de tablas
- Exportar/importar datos

**Nota**: Adminer se conecta directamente al contenedor de PostgreSQL usando el nombre del servicio `db`, por lo que no se necesita usar `localhost:5433`.
