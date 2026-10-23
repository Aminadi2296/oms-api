from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import Company, User, WorkflowStage
from app.schemas.stage import StageCreate, StageOut

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
