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

## Etapas de empresa

Para listar las etapas, envía `GET /api/v1/companies/{company_id}/stages` con un token Bearer. La respuesta es un array ordenado por `position`, y la empresa debe coincidir con la del usuario autenticado.

Para crear una etapa, envía `POST /api/v1/companies/{company_id}/stages` con un token Bearer y un cuerpo como:

```json
{
  "name": "En revisión",
  "is_final": false
}
```

La empresa debe coincidir con la del usuario autenticado. El servidor asigna `company_id` y la siguiente `position`; `is_final` se guarda en el campo interno `is_completed_stage`. La respuesta incluye `id`, `company_id`, `name`, `position` e `is_final`.
