from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import Company, Order, User, WorkflowStage
from app.schemas.stage import StageCreate, StageOut, StageUpdate

router = APIRouter(prefix="/companies", tags=["Stages"])


@router.get("/{company_id}/stages", response_model=list[StageOut])
async def list_stages(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=403, detail="El usuario no pertenece a una empresa")

    company_result = await db.execute(
        select(Company.id).where(
            Company.id == company_id,
            Company.id == current_user.company_id,
        )
    )
    if company_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    result = await db.execute(
        select(WorkflowStage)
        .where(WorkflowStage.company_id == company_id)
        .order_by(WorkflowStage.position, WorkflowStage.id)
    )
    return result.scalars().all()


@router.post(
    "/{company_id}/stages",
    response_model=StageOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_stage(
    company_id: int,
    payload: StageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=403, detail="El usuario no pertenece a una empresa")

    company_result = await db.execute(
        select(Company)
        .where(
            Company.id == company_id,
            Company.id == current_user.company_id,
        )
        .with_for_update()
    )
    company = company_result.scalars().first()
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    last_position = await db.scalar(
        select(func.max(WorkflowStage.position)).where(
            WorkflowStage.company_id == company.id
        )
    )
    stage = WorkflowStage(
        company_id=company.id,
        name=payload.name,
        position=(last_position + 1) if last_position is not None else 0,
        is_completed_stage=payload.is_final,
    )
    db.add(stage)
    await db.commit()
    await db.refresh(stage)
    return stage


@router.put("/{company_id}/stages/{stage_id}", response_model=StageOut)
@router.patch("/{company_id}/stages/{stage_id}", response_model=StageOut)
async def update_stage(
    company_id: int,
    stage_id: int,
    payload: StageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.company_id is None or current_user.company_id != company_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta empresa")

    result = await db.execute(
        select(WorkflowStage).where(
            WorkflowStage.id == stage_id,
            WorkflowStage.company_id == company_id,
        )
    )
    stage = result.scalars().first()
    if stage is None:
        raise HTTPException(status_code=404, detail="Etapa no encontrada")

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] is not None:
        stage.name = update_data["name"]
    if "position" in update_data and update_data["position"] is not None:
        stage.position = update_data["position"]
    if "is_final" in update_data and update_data["is_final"] is not None:
        stage.is_completed_stage = update_data["is_final"]

    await db.commit()
    await db.refresh(stage)
    return stage


@router.delete("/{company_id}/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stage(
    company_id: int,
    stage_id: int,
    force: Optional[str] = Query(None),
    reassign_to: Optional[int] = Query(None, alias="reassignTo"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.company_id is None or current_user.company_id != company_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta empresa")

    result = await db.execute(
        select(WorkflowStage).where(
            WorkflowStage.id == stage_id,
            WorkflowStage.company_id == company_id,
        )
    )
    stage = result.scalars().first()
    if stage is None:
        raise HTTPException(status_code=404, detail="Etapa no encontrada")

    orders_count = await db.scalar(
        select(func.count(Order.id)).where(
            Order.stage_id == stage_id,
            Order.company_id == company_id,
        )
    ) or 0

    if orders_count > 0:
        if reassign_to is not None:
            if reassign_to == stage_id:
                raise HTTPException(status_code=400, detail="La etapa de destino debe ser distinta a la eliminada")

            target_result = await db.execute(
                select(WorkflowStage).where(
                    WorkflowStage.id == reassign_to,
                    WorkflowStage.company_id == company_id,
                )
            )
            target_stage = target_result.scalars().first()
            if target_stage is None:
                raise HTTPException(status_code=404, detail="Etapa de destino no encontrada")

            await db.execute(
                update(Order)
                .where(Order.stage_id == stage_id, Order.company_id == company_id)
                .values(
                    stage_id=target_stage.id,
                    completed_at=datetime.utcnow() if target_stage.is_completed_stage else None,
                )
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar la etapa porque tiene {orders_count} pedido(s). Mueve o elimina los pedidos primero.",
            )

    await db.delete(stage)
    await db.commit()
