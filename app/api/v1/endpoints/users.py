from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models import Company, Order, User, UserRole
from app.schemas.user import TeamMemberCreate, TeamMemberOut, TeamMemberUpdate

router = APIRouter(prefix="/companies", tags=["Team / Users"])


def _ensure_company_access(current_user: User, company_id: int, require_admin: bool = False):
    if current_user.role != UserRole.SUPERADMIN:
        if current_user.company_id is None or current_user.company_id != company_id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta empresa")
        if require_admin and current_user.role != UserRole.COMPANY_ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Solo el administrador de la empresa puede gestionar miembros del equipo",
            )


async def _get_order_counts_by_user(db: AsyncSession, company_id: int) -> dict[int, tuple[int, int]]:
    stmt = (
        select(
            Order.assigned_to_id,
            func.sum(case((Order.completed_at.is_(None), 1), else_=0)).label("active_count"),
            func.sum(case((Order.completed_at.is_not(None), 1), else_=0)).label("completed_count"),
        )
        .where(Order.company_id == company_id, Order.assigned_to_id.is_not(None))
        .group_by(Order.assigned_to_id)
    )
    rows = (await db.execute(stmt)).all()
    return {
        int(row.assigned_to_id): (int(row.active_count or 0), int(row.completed_count or 0))
        for row in rows
    }


def _serialize_member(user: User, counts: tuple[int, int] = (0, 0)) -> TeamMemberOut:
    active_count, completed_count = counts
    return TeamMemberOut(
        id=user.id,
        company_id=user.company_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        job_title=user.job_title,
        phone=user.phone,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        created_at=user.created_at,
        active_orders_count=active_count,
        completed_orders_count=completed_count,
    )


@router.get("/{company_id}/users", response_model=list[TeamMemberOut])
async def list_company_users(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_company_access(current_user, company_id, require_admin=False)

    company_exists = await db.scalar(select(Company.id).where(Company.id == company_id))
    if company_exists is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    result = await db.execute(
        select(User)
        .where(User.company_id == company_id)
        .order_by(User.is_active.desc(), User.full_name.asc(), User.id.asc())
    )
    users = result.scalars().all()
    counts_map = await _get_order_counts_by_user(db, company_id)

    return [_serialize_member(u, counts_map.get(u.id, (0, 0))) for u in users]


@router.post(
    "/{company_id}/users",
    response_model=TeamMemberOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_company_user(
    company_id: int,
    payload: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_company_access(current_user, company_id, require_admin=True)

    company = await db.scalar(select(Company).where(Company.id == company_id))
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    existing = await db.scalar(select(User.id).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=400, detail="Este correo electrónico ya está registrado")

    allowed_role = payload.role if payload.role in (UserRole.COMPANY_ADMIN, UserRole.EMPLOYEE) else UserRole.EMPLOYEE

    user = User(
        company_id=company_id,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=allowed_role,
        job_title=payload.job_title or None,
        phone=payload.phone or None,
        avatar_url=payload.avatar_url or None,
        is_active=payload.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return _serialize_member(user, (0, 0))


@router.patch("/{company_id}/users/{user_id}", response_model=TeamMemberOut)
@router.put("/{company_id}/users/{user_id}", response_model=TeamMemberOut)
async def update_company_user(
    company_id: int,
    user_id: int,
    payload: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_company_access(current_user, company_id, require_admin=True)

    user = await db.scalar(
        select(User).where(User.id == user_id, User.company_id == company_id)
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Miembro del equipo no encontrado")

    update_data = payload.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] and update_data["email"] != user.email:
        email_taken = await db.scalar(
            select(User.id).where(User.email == update_data["email"], User.id != user_id)
        )
        if email_taken is not None:
            raise HTTPException(status_code=400, detail="Este correo electrónico ya está en uso")
        user.email = update_data["email"]

    if "full_name" in update_data and update_data["full_name"] is not None:
        user.full_name = update_data["full_name"]

    if "job_title" in update_data:
        user.job_title = update_data["job_title"] or None

    if "phone" in update_data:
        user.phone = update_data["phone"] or None

    if "avatar_url" in update_data:
        user.avatar_url = update_data["avatar_url"] or None

    if "role" in update_data and update_data["role"] is not None:
        if user.id == current_user.id and update_data["role"] != user.role:
            raise HTTPException(status_code=400, detail="No puedes cambiar tu propio nivel de acceso")
        if update_data["role"] in (UserRole.COMPANY_ADMIN, UserRole.EMPLOYEE):
            user.role = update_data["role"]

    if "is_active" in update_data and update_data["is_active"] is not None:
        if user.id == current_user.id and not update_data["is_active"]:
            raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")
        user.is_active = update_data["is_active"]

    if "password" in update_data and update_data["password"]:
        user.hashed_password = get_password_hash(update_data["password"])

    await db.commit()
    await db.refresh(user)

    counts_map = await _get_order_counts_by_user(db, company_id)
    return _serialize_member(user, counts_map.get(user.id, (0, 0)))


@router.delete("/{company_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_user(
    company_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_company_access(current_user, company_id, require_admin=True)

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario")

    user = await db.scalar(
        select(User).where(User.id == user_id, User.company_id == company_id)
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Miembro del equipo no encontrado")

    await db.delete(user)
    await db.commit()
