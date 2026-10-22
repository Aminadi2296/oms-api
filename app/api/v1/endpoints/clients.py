import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.db.session import get_db
from app.models import Customer, User
from app.core.dependencies import get_current_user
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut

router = APIRouter(prefix="/clients", tags=["Clients"])


class PaginationMeta(BaseModel):
    current_page: int
    last_page: int
    per_page: int
    total: int


class PaginatedCustomersResponse(BaseModel):
    clients: List[CustomerOut]
    data: List[CustomerOut]
    total: int
    page: int
    per_page: int
    pages: int
    meta: PaginationMeta


@router.get("", response_model=PaginatedCustomersResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista de clientes filtrados por tenant (empresa) con paginación que el frontend espera"""
    query = select(Customer).where(Customer.company_id == current_user.company_id)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Customer.razon_social.ilike(search_filter),
                Customer.nombre_comercial.ilike(search_filter),
                Customer.numero_fiscal.ilike(search_filter),
                Customer.correo_principal.ilike(search_filter),
            )
        )

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Paginación
    offset = (page - 1) * per_page
    query = query.order_by(Customer.id.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    customers = result.scalars().all()

    last_page = math.ceil(total / per_page) if total > 0 else 1

    return {
        "clients": customers,
        "data": customers,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": last_page,
        "meta": {
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
        },
    }


@router.get("/search", response_model=PaginatedCustomersResponse)
async def search_customers(
    query: Optional[str] = Query(None, alias="query"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Búsqueda de clientes compatible con useClientSearch del frontend"""
    return await list_customers(
        page=page,
        per_page=per_page,
        search=query,
        db=db,
        current_user=current_user,
    )


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un cliente asociado a la empresa del usuario autenticado"""
    customer_data = payload.model_dump()
    customer = Customer(
        company_id=current_user.company_id,
        **customer_data,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.company_id == current_user.company_id,
        )
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer
