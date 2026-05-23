# Docker & Deployment en Railway

## 📦 Archivos Docker

| Archivo | Propósito |
|---------|-----------|
| `Dockerfile` | Imagen Docker de la aplicación (producción) |
| `docker-compose.yml` | Orquestación local con MySQL (desarrollo) |
| `.dockerignore` | Archivos excluidos del build |
| `.env.example` | Plantilla de variables de entorno |
| `Procfile` | Definición del comando de inicio (Railway) |

---

## 🔨 Desarrollo con Docker Compose

### Levantar el proyecto completo

```bash
docker-compose up --build
```

Esto inicia:
- **MySQL 8.0** en `localhost:3306`
- **Flask app** en `localhost:5000`

**Credenciales por defecto:**
```
Usuario: usuario
Contraseña: contraseña
Base de datos: gestion_educativa
```

### Comandos útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f web

# Ejecutar comandos en el contenedor
docker-compose exec web pytest src/

# Detener contenedores
docker-compose down

# Eliminar volúmenes (borra la BD)
docker-compose down -v
```

### Variables de entorno

Se definen en `docker-compose.yml`. Cambiar según necesites:

```yaml
environment:
  DATABASE_URL: mysql://usuario:contraseña@db:3306/gestion_educativa
  FLASK_ENV: development
  JWT_SECRET_KEY: dev-secret-key-change-in-production
```

---

## 🚀 Deployment en Railway

### Requisitos previos

1. Crear cuenta en [railway.app](https://railway.app)
2. Tener un repositorio GitHub con el código
3. Configurar una base de datos MySQL (en Railway o externa)

### Pasos de deployment

#### 1. Conectar repositorio

```
Railway Dashboard → New Project → GitHub
```

Seleccionar el repositorio y Railway detectará automáticamente:
- Python 3.11 (por `requirements.txt`)
- Procfile (comando de inicio)
- Dockerfile (si lo prefieres)

#### 2. Configurar variables de entorno

En Railway → Variables → Agregar:

| Variable | Valor | Ejemplo |
|----------|-------|---------|
| `DATABASE_URL` | Conexión MySQL | `mysql://user:pass@host:port/db` |
| `JWT_SECRET_KEY` | Clave aleatoria segura | Generar con `openssl rand -hex 32` |
| `FLASK_ENV` | `production` | `production` |

**Generar JWT_SECRET_KEY segura:**
```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
[Convert]::ToHexString((1..32 | ForEach-Object {Get-Random -Maximum 256}))
```

#### 3. Base de datos MySQL en Railway

Railway proporciona MySQL como servicio. Para agregarlo:

```
Project → Add Service → MySQL
```

Railway generará automáticamente la `DATABASE_URL`. Solo cópiala a Variables.

#### 4. Deployment automático

Hacer push a la rama principal:

```bash
git push origin main
```

Railway construirá y desplegará automáticamente. Ver progreso en:

```
Project → Deployments → [tu deployment]
```

---

## 📋 Flujo de una solicitud en producción

```
Cliente HTTPS
    ↓
Railway Load Balancer (SSL/TLS)
    ↓
Gunicorn workers (4 procesos)
    ↓
Flask app → Use cases → MySQL
```

**Puerto:** Railway asigna automáticamente el puerto a través de la variable `$PORT`.

---

## ⚙️ Configuración de Gunicorn

En `Procfile`:

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 30 app:app
```

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `--bind` | `0.0.0.0:$PORT` | Escucha en todos los interfaces, puerto asignado por Railway |
| `--workers` | `4` | Número de procesos worker (ajusta según disponibilidad) |
| `--worker-class` | `sync` | Tipo de worker síncrono (simple y estable) |
| `--timeout` | `30` | Timeout en segundos por request |

---

## 🔍 Logs en Railway

```
Project → Deployments → [tu deployment] → Logs
```

Filtrar por nivel:
- `Error` — Errores de aplicación
- `Warning` — Advertencias
- `Info` — Información general
- `Debug` — Información detallada

---

## 🐛 Troubleshooting

### Error: Database connection refused
**Causa:** `DATABASE_URL` incorrecta o BD no accesible.
**Solución:**
- Verificar `DATABASE_URL` en Variables
- Confirmar que MySQL está corriendo
- Si es externa, verificar firewall/reglas de red

### Error: 502 Bad Gateway
**Causa:** App crasheó o no inició correctamente.
**Solución:**
- Ver logs en Railway
- Verificar que `requirements.txt` tiene todas las dependencias
- Asegurar que `Procfile` tiene el comando correcto

### Error: 504 Gateway Timeout
**Causa:** Request toma más de 30 segundos.
**Solución:**
- Aumentar `--timeout` en Procfile si las queries son lentas
- Optimizar queries SQL
- Considerar usar caching

---

## 📊 Monitoreo

Railway proporciona:
- **CPU/Memory** — Usar menos workers si está al límite
- **Network** — Monitorear ancho de banda
- **Deployment history** — Historial de despliegues

---

## 🔐 Seguridad

✅ **Hacer en producción:**
- ✅ Cambiar `JWT_SECRET_KEY` a valor aleatorio
- ✅ Usar HTTPS (Railway lo proporciona automáticamente)
- ✅ Configurar firewall en MySQL (solo desde Railway)
- ✅ Revisar logs regularmente
- ✅ Mantener dependencias actualizadas

❌ **NO hacer:**
- ❌ Hardcodear secrets en el código
- ❌ Usar contraseñas débiles en `DATABASE_URL`
- ❌ Dejar `FLASK_ENV=development` en producción
- ❌ Exponer variables secretas en logs

---

## 📚 Referencias

- [Railway Docs](https://docs.railway.app)
- [Gunicorn Docs](https://gunicorn.org)
- [Docker Compose Docs](https://docs.docker.com/compose)
- [Flask Deployment](https://flask.palletsprojects.com/en/3.0.x/deployment/)
