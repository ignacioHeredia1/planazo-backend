# 🎯 Planazo

Plataforma web dinámica e interactiva para descubrir, filtrar y generar planes y actividades según tus preferencias. 

![Planazo App](app/static/icon.png) <!-- Reemplazar si hay captura de pantalla -->

---

## 🚀 Características y Funcionalidades Avanzadas

El proyecto destaca por incorporar funcionalidades completas tanto en el frontend como en el backend:

- **🔐 Sistema de Usuarios y Favoritos:** Registro, inicio de sesión seguro (contraseñas hasheadas) y gestión de perfiles donde los usuarios pueden guardar sus planes favoritos o descartar los que no les gustan.
- **🤖 Generación de Planes con IA:** Integración con Gemini AI para generar automáticamente nuevos planes si no hay resultados en la base de datos que coincidan con los filtros del usuario.
- **🌤️ Clima en Tiempo Real:** Integración con OpenWeather API. Permite filtrar planes por el clima ideal, y al entrar al detalle del plan, obtiene el clima en vivo de la ciudad y emite recomendaciones dinámicas.
- **🗺️ Mapas Geográficos:** Integración nativa con Leaflet.js y OpenStreetMap para mostrar la ubicación exacta de los planes con pines dinámicos en mapas interactivos.
- **🌙 Modo Oscuro (Dark Mode):** Interfaz fluida con variables CSS dinámicas y persistencia en el navegador mediante `localStorage` para evitar el "Flash of Unstyled Content" (FOUC).
- **🔔 Notificaciones asíncronas (Toasts):** Intercepción de formularios con JavaScript (`fetch` API) para agregar a favoritos sin recargar la página, brindando una experiencia "app-like".
- **📊 Panel de Administración Dashboard:** Sección exclusiva para administradores con un panel de estadísticas generales (SQL `COUNT`, `AVG`, `GROUP BY`) y gestión completa (CRUD) de planes.
- **🖼️ Subida de Imágenes Reales (File Upload):** Permite subir archivos multimedia en formato binario desde el panel de admin al servidor local (`multipart/form-data`).

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python + FastAPI
- **Base de Datos:** SQLite (ORM: SQLAlchemy)
- **Frontend:** Jinja2 Templates, HTML5, Vanilla CSS avanzado, JavaScript (ES6)
- **APIs Externas:** OpenWeatherMap, OpenStreetMap, Google Gemini AI

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/planazo.git
cd planazo
```

### 2. Crear y activar el entorno virtual
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate

### 3. Instalar dependencias
Asegurate de instalar todas las dependencias listadas en `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Variables de entorno
Debes tener las siguientes claves en tu código o como variables de entorno:
- `GEMINI_API_KEY`: Clave para la generación de IA.
- `WEATHER_API_KEY`: Clave de OpenWeather (actualmente en código).

### 5. Ejecutar el servidor
```bash
uvicorn app.main:app --reload
```
La plataforma estará disponible en `http://127.0.0.1:8000`.

---

## 🔑 Credenciales por Defecto

**Administrador**
- **Usuario:** `admin`
- **Contraseña:** `planazo123`

*(Para probar el panel de control y la subida de imágenes, dirigite a `/admin`)*

---
Desarrollado como proyecto académico de Desarrolo de Software.