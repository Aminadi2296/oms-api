import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import Customer, Order, User, WorkflowStage
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate

router = APIRouter(prefix="/orders", tags=["Orders"])


class PaginationMeta(BaseModel):
    current_page: int
    last_page: int
    per_page: int
    total: int


class PaginatedOrdersResponse(BaseModel):
    orders: list[OrderOut]
    data: list[OrderOut]
    total: int
    page: int
    per_page: int
    pages: int
    meta: PaginationMeta


async def _validate_order_relations(
    db: AsyncSession,
    company_id: int,
    customer_id: Optional[int] = None,
    stage_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
):
    stage = None

    if customer_id is not None:
        customer_result = await db.execute(
            select(Customer.id).where(
                Customer.id == customer_id,
                Customer.company_id == company_id,
            )
        )
        if customer_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if stage_id is not None:
        stage_result = await db.execute(
            select(WorkflowStage).where(
                WorkflowStage.id == stage_id,
                WorkflowStage.company_id == company_id,
            )
        )
        stage = stage_result.scalars().first()
        if stage is None:
            raise HTTPException(status_code=404, detail="Etapa no encontrada")

    if assigned_to_id is not None:
        user_result = await db.execute(
            select(User.id).where(
                User.id == assigned_to_id,
                User.company_id == company_id,
            )
        )
        if user_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Usuario asignado no encontrado")

    return stage


@router.get("", response_model=PaginatedOrdersResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=403, detail="El usuario no pertenece a una empresa")

    query = select(Order).where(Order.company_id == current_user.company_id)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Order.order_number.ilike(search_filter),
                Order.title.ilike(search_filter),
                Order.description.ilike(search_filter),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * per_page
    query = query.order_by(Order.updated_at.desc(), Order.id.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    orders = result.scalars().all()

    last_page = math.ceil(total / per_page) if total > 0 else 1

    return {
        "orders": orders,
        "data": orders,
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


@router.get("/search", response_model=PaginatedOrdersResponse)
async def search_orders(
    query: Optional[str] = Query(None, alias="query"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_orders(
        page=page,
        per_page=per_page,
        search=query,
        db=db,
        current_user=current_user,
    )


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=403, detail="El usuario no pertenece a una empresa")

    stage = await _validate_order_relations(
        db=db,
        company_id=current_user.company_id,
        customer_id=payload.customer_id,
        stage_id=payload.stage_id,
        assigned_to_id=payload.assigned_to_id,
    )

    next_number = await db.scalar(
        select(func.count(Order.id)).where(Order.company_id == current_user.company_id)
    )
    order_number = f"ORD-{(next_number or 0) + 1:04d}"

    order = Order(
        company_id=current_user.company_id,
        order_number=order_number,
        title=payload.title,
        description=payload.description,
        customer_id=payload.customer_id,
        stage_id=payload.stage_id,
        assigned_to_id=payload.assigned_to_id,
        priority=payload.priority,
        deadline=payload.deadline,
        position=payload.position,
        completed_at=datetime.utcnow() if stage and stage.is_completed_stage else None,
    )

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=403, detail="El usuario no pertenece a una empresa")

    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.company_id == current_user.company_id,
        )
    )
    order = result.scalars().first()
    if order is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order


@router.patch("/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=403, detail="El usuario no pertenece a una empresa")

    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.company_id == current_user.company_id,
        )
    )
    order = result.scalars().first()
    if order is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    update_data = payload.model_dump(exclude_unset=True)

    if "customer_id" in update_data and update_data["customer_id"] is not None:
        await _validate_order_relations(
            db=db,
            company_id=current_user.company_id,
            customer_id=update_data["customer_id"],
        )

    if "stage_id" in update_data and update_data["stage_id"] is not None:
        stage = await _validate_order_relations(
            db=db,
            company_id=current_user.company_id,
            stage_id=update_data["stage_id"],
        )
        update_data["completed_at"] = datetime.utcnow() if stage.is_completed_stage else None

    if "assigned_to_id" in update_data and update_data["assigned_to_id"] is not None:
        await _validate_order_relations(
            db=db,
            company_id=current_user.company_id,
            assigned_to_id=update_data["assigned_to_id"],
        )

    for field, value in update_data.items():
        setattr(order, field, value)

    await db.commit()
    await db.refresh(order)
    return order
