# Sistema de Gestión Educativa
## Instalación

```bash
git clone <repo-url>
cd Sistema_gestion_educativa

python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

## Configuración

```bash
cp .env.example .env
```

## Ejecutar Backend

```bash
python app.py
```
## Ejecutar Frontend

```bash
python frontend/app.py
```

## O tambien

```bash
cd frontend
python app.py
```

Backend disponible en `http://localhost:5000`
Frontend disponible en `http://localhost:5001`


Ruta para probar asistencia como alumno http://127.0.0.1:5001/aulas/cambiarPorNumeroDeAula/asistencia/validar?code=  <-- ahi va el codigo que se consigue desde assistencia como profesor

