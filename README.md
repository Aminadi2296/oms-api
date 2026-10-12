# OMS Backend API (FastAPI + PostgreSQL)

API Multi-tenant para el Sistema de Gestión de Pedidos (OMS) con tableros Kanban, métricas y control de suscripciones.

## Requisitos
* Python 3.10+
* PostgreSQL

## Instalación y Ejecución Local

1. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   ```

2. **Activar entorno virtual:**
   * En Windows:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * En Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   * Copiar `.env.example` a `.env` y ajustar las credenciales de PostgreSQL.

5. **Iniciar el servidor de desarrollo:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Documentación interactiva Swagger:**
   * Abrir en el navegador: [http://localhost:8000/docs](http://localhost:8000/docs)
