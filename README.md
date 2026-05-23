# Sistema de Gestión Educativa

## Requisitos

- Python 3.11+
- MySQL 8.0+

## Instalación

```bash
git clone <repo-url>
cd Sistema_gestion_educativa

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

## Configuración

```bash
cp .env.example .env
```

Completar `.env` con las credenciales de la base de datos:

```env
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/gestion_educativa
```

Ejecutar en MySQL:

```sql
CREATE TABLE IF NOT EXISTS sesiones_activas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    token VARCHAR(500) NOT NULL UNIQUE,
    expira_en DATETIME NOT NULL,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES users(id)
);
```

## Ejecutar

```bash
python app.py
```

Disponible en `http://localhost:5000`
