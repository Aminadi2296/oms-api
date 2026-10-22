import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models import User, Company, Customer

async def check():
    async with AsyncSessionLocal() as session:
        users = (await session.execute(select(User))).scalars().all()
        companies = (await session.execute(select(Company))).scalars().all()
        customers = (await session.execute(select(Customer))).scalars().all()
        print('=== USERS ===')
        for u in users:
            print(f'User ID: {u.id}, Email: {u.email}, Company ID: {u.company_id}, Role: {u.role}')
        print('=== COMPANIES ===')
        for c in companies:
            print(f'Company ID: {c.id}, Name: {c.name}')
        print('=== CUSTOMERS ===')
        for cust in customers:
            print(f'Customer ID: {cust.id}, Razon Social: {cust.razon_social}, Company ID: {cust.company_id}')

if __name__ == '__main__':
    asyncio.run(check())
