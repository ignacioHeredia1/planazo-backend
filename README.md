# 🎯 Planazo

Plataforma web para encontrar planes y actividades según tus preferencias. Filtrá por hora, presupuesto, cantidad de personas, mascotas, clima y distancia.

---

## 🛠️ Tecnologías

- **Backend**: Python + FastAPI
- **Base de datos**: SQLite (archivo `planify.db`)
- **Frontend**: HTML + CSS con Jinja2
- **APIs externas**: OpenWeatherMap (clima), OpenStreetMap (mapas)

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/planazo.git
cd planazo
```

### 2. Crear el entorno virtual

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Cargar datos de prueba

```bash
python seed.py
```

### 6. Correr el servidor

```bash
uvicorn app.main:app --reload
```

### 7. Abrir en el navegador

```
http://localhost:8000
```

---

## 🗂️ Estructura del proyecto

```
planazo/
├── app/
│   ├── templates/        # Páginas HTML (Jinja2)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── admin.html
│   │   ├── admin_form.html
│   │   ├── login.html
│   │   ├── login_usuario.html
│   │   ├── registro.html
│   │   └── perfil.html
│   ├── static/
│   │   └── style.css     # Estilos
│   ├── __init__.py
│   ├── main.py           # Rutas y lógica principal
│   ├── models.py         # Tablas de la base de datos
│   ├── schemas.py        # Validación de datos
│   ├── database.py       # Conexión a la base de datos
│   └── clima.py          # Integración con OpenWeatherMap
├── venv/                 # Entorno virtual (no se sube a GitHub)
├── seed.py               # Script para cargar datos de prueba
├── requirements.txt      # Dependencias del proyecto
├── .env                  # Variables de entorno (no se sube a GitHub)
├── .gitignore
└── README.md
```

---

## 📌 Páginas principales

| URL | Descripción |
|-----|-------------|
| `/` | Página principal con filtros y planes |
| `/registro` | Crear cuenta de usuario |
| `/login` | Iniciar sesión |
| `/perfil` | Ver y gestionar favoritos |
| `/admin` | Panel de administración (requiere login) |
| `/admin/login` | Login del administrador |

---

## 🔐 Credenciales de administrador

> **Importante**: Cambiar estas credenciales antes de subir a producción.

Las credenciales están definidas en `app/main.py`:

```python
ADMIN_USUARIO = "admin"
ADMIN_PASSWORD = "planazo123"
```

---

## 👥 Tipos de usuario

| Tipo | Descripción |
|------|-------------|
| **Visitante** | Accede sin registrarse. Puede buscar y descartar planes. |
| **Usuario registrado** | Puede guardar planes en favoritos y ver su perfil. |
| **Administrador** | Puede agregar, editar y eliminar planes desde el panel. |

---

## 📦 Dependencias principales

```
fastapi
uvicorn[standard]
sqlalchemy
pydantic[email]
jinja2
python-multipart
httpx
python-dotenv
itsdangerous
passlib[bcrypt]
bcrypt==4.0.1
```