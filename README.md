# Sistema de Gestión Educativa

Backend del Sistema de Gestión Educativa construido con Flask y Arquitectura Hexagonal.

## 🚀 Inicio Rápido

### Requisitos previos

- **Python 3.11+**
- **MySQL 8.0+** (o MariaDB 10.5+)
- **Git**
- **Docker & Docker Compose** (opcional, para containerización)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repo-url>
   cd Sistema_gestion_educativa
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   ```
   Editar `.env` con tus credenciales:
   ```env
   DATABASE_URL=mysql://usuario:contraseña@localhost/gestion_educativa
   FLASK_ENV=development
   JWT_SECRET_KEY=tu-clave-secreta-aqui
   ```

5. **Ejecutar el servidor**
   ```bash
   python app.py
   ```
   El servidor estará disponible en `http://localhost:5000`

---

## 🐳 Docker

### Con Docker Compose (recomendado para desarrollo)

```bash
# Construir e iniciar contenedores
docker-compose up --build

# En otra terminal, ejecutar migraciones (si es necesario)
docker-compose exec web python -c "from src.repositories.classroom.list_classroom_teachers import ClassroomTeachersRepository; print('DB ready')"

# Detener contenedores
docker-compose down

# Ver logs
docker-compose logs -f web
```

La base de datos MySQL estará disponible en `localhost:3306` con las credenciales del `docker-compose.yml`.

### Con Docker (solo aplicación)

```bash
# Construir imagen
docker build -t gestion-educativa:latest .

# Ejecutar contenedor
docker run -p 5000:5000 \
  -e DATABASE_URL=mysql://usuario:contraseña@host:3306/db \
  -e JWT_SECRET_KEY=tu-clave-secreta \
  gestion-educativa:latest
```

---

## 🚀 Deployment en Railway

### Pasos para desplegar:

1. **Crear cuenta en [Railway.app](https://railway.app)**

2. **Conectar repositorio:**
   - En Railway Dashboard → New Project → GitHub
   - Seleccionar tu repositorio

3. **Configurar variables de entorno:**
   - En Railway, ir a Variables
   - Agregar las siguientes variables:
     ```
     DATABASE_URL=mysql://usuario:password@host:port/db
     JWT_SECRET_KEY=generar-una-clave-aleatoria-segura
     FLASK_ENV=production
     ```

4. **Railway detectará automáticamente:**
   - `Procfile` para el comando de inicio
   - `requirements.txt` para las dependencias
   - Puerto automáticamente asignado (usa $PORT)

5. **Desplegar:**
   - Hacer push a la rama principal
   - Railway construirá y desplegará automáticamente

**Nota:** Railway incluye MySQL como servicio adicional si lo necesitas. Configura la `DATABASE_URL` en el panel de Railway.

---

## 📁 Estructura del Proyecto

```
src/
├── app/                      # Configuración y orchestración
│   └── router.py            # Blueprint de classroom
├── core/
│   ├── contracts/           # DTOs y puertos
│   │   ├── request/         # Modelos de entrada
│   │   └── response/        # Modelos de salida
│   ├── entities/            # Modelos de dominio (TypedDict)
│   └── usecase/             # Lógica de negocio
├── entrypoints/             # Adapters de entrada (Flask handlers)
│   ├── auth/
│   └── classroom/
│       ├── classroom.py            # List professors handler
│       └── delete_classroom_user.py # Delete user handler
├── providers/               # Inyección de dependencias
│   ├── auth/
│   └── classroom/
├── repositories/            # Adapters de salida (SQL)
│   ├── auth/
│   └── classroom/
└── dependencies/            # Configuración de dependencias

docs/                         # Documentación de endpoints
├── list_classroom_professors.md
└── delete_classroom_user.md

tests/                        # Pruebas unitarias
app.py                        # Punto de entrada de la aplicación
requirements.txt              # Dependencias de Python
```

---

## 🔧 Comandos útiles

### Tests
```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=src

# Ejecutar un archivo de test específico
pytest src/repositories/classroom/test_delete_classroom_user.py
```

### Linting y Formato
```bash
# Verificar con Ruff (linter)
ruff check .

# Arreglar automáticamente con Ruff
ruff check --fix .

# Formatear código con Ruff
ruff format .

# Verificar tipos con MyPy
mypy src/
```

### Base de Datos
```bash
# Crear la base de datos
mysql -u usuario -p < migrations/init.sql

# Ver status de la conexión
python -c "from src.repositories.classroom.list_classroom_teachers import ClassroomTeachersRepository; r = ClassroomTeachersRepository(); print('DB connected')"
```

---

## 📝 Endpoints disponibles

### Classroom - List Professors
```
GET /classrooms/{classroom_id}/professors
Authorization: Bearer <token>
```
**Descripción:** Obtiene la lista de profesores en un classroom.  
**Documentación:** Ver [`docs/list_classroom_professors.md`](docs/list_classroom_professors.md)

### Classroom - Delete User
```
DELETE /api/v1/classrooms/{classroom_id}/user/{user_id}
Authorization: Bearer <token>
```
**Descripción:** Elimina un usuario de un classroom (requiere rol Admin).  
**Documentación:** Ver [`docs/delete_classroom_user.md`](docs/delete_classroom_user.md)

---

## 🏗️ Arquitectura

El proyecto sigue **Arquitectura Hexagonal (Ports & Adapters)** con capas:

```
Entrypoints (HTTP)
    ↓
Use Cases (Lógica de negocio)
    ↓
Repositories (SQL)
    ↓
Database
```

**Patrones:**
- **Single Responsibility Principle (SRP):** Cada clase tiene una única responsabilidad
- **Dependency Injection:** Los providers inyectan dependencias en los use cases
- **Guard Clauses:** Validaciones al inicio de funciones
- **Type Hints:** Código con tipos explícitos para mejor mantenibilidad
- **Error Centralization:** Errores definidos como constantes en `errors.py`

---

## 🔐 Autenticación

Los endpoints usan **JWT (JSON Web Token)** para autenticar solicitudes:

1. El cliente incluye el token en el header: `Authorization: Bearer <token>`
2. El `VerifyTokenUseCase` valida la firma y comprueba la sesión activa
3. Si el token es válido, la solicitud continúa; si no, se retorna **401 Unauthorized**

**Almacenamiento de sesiones:** In-memory cache (no persistente entre reinicios).

---

## 🧪 Testing

Las pruebas siguen estándares:
- **Mínimo 80% de cobertura** en archivos modificados
- **Un test por rama lógica** (use cases, validaciones)
- **Mocking de repositorios** para aislar lógica
- **Nombres descriptivos** que expliquen qué se prueba

### Ejecutar pruebas específicas
```bash
# Tests del endpoint DELETE
pytest src/repositories/classroom/test_delete_classroom_user.py -v

# Con cobertura detallada
pytest src/ --cov=src --cov-report=html
```

---

## 📌 Notas importantes

- **ADMIN_ROLE_ID:** Actualmente configurado como `1` en `delete_classroom_user.py`. Ajustar según tu schema de roles.
- **DATABASE_URL:** Debe usar el formato `mysql://usuario:contraseña@host/db`.
- **JWT_SECRET_KEY:** Cambiar en producción con una clave segura y aleatoria.
- **Entorno:** En desarrollo usa `FLASK_ENV=development` para debug automático.

---

## 📚 Documentación adicional

- [`docs/list_classroom_professors.md`](docs/list_classroom_professors.md) — Endpoint GET /classrooms/{id}/professors
- [`docs/delete_classroom_user.md`](docs/delete_classroom_user.md) — Endpoint DELETE /api/v1/classrooms/{id}/user/{id}
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — Guía completa de arquitectura y estándares

---

## 🤝 Contribuciones

1. Crear una rama: `git checkout -b feature/nueva-funcionalidad`
2. Realizar cambios y pasar tests: `pytest`
3. Verificar tipos: `mypy src/`
4. Formatear: `ruff format .`
5. Hacer commit: `git commit -m "feat: descripción"`
6. Push: `git push origin feature/nueva-funcionalidad`
7. Abrir Pull Request

---

## 📄 Licencia

Proyecto educativo - Todos los derechos reservados.
