import asyncio
from app.db.session import engine, Base
import app.models  # Importa todos los modelos para registrarlos

async def create_tables():
    async with engine.begin() as conn:
        print("Creando tablas en PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)
        print("¡Tablas creadas exitosamente!")

if __name__ == "__main__":
    asyncio.run(create_tables())
