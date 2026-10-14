from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models import User, Company, WorkflowStage, UserRole
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user
from app.schemas.auth import Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut)
async def register_company_and_admin(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verificar si el email ya existe
    existing_user = await db.execute(select(User).where(User.email == payload.email))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="Este correo ya se encuentra registrado.")

    # 1. Crear Empresa (Tenant)
    slug = payload.company_name.lower().replace(" ", "-")
    company = Company(
        name=payload.company_name,
        slug=slug,
        subscription_plan="STARTER",
        max_users=5,
    )
    db.add(company)
    await db.flush()

    # 2. Crear Columnas iniciales por defecto para el Kanban de esta empresa
    default_stages = [
        {"name": "Nuevo Pedido", "position": 0, "color": "#3b82f6", "is_completed_stage": False},
        {"name": "En Proceso", "position": 1, "color": "#f59e0b", "is_completed_stage": False},
        {"name": "Control de Calidad", "position": 2, "color": "#8b5cf6", "is_completed_stage": False},
        {"name": "Finalizado", "position": 3, "color": "#10b981", "is_completed_stage": True},
    ]
    for stage_data in default_stages:
        db.add(WorkflowStage(company_id=company.id, **stage_data))

    # 3. Crear Usuario Administrador de la Empresa
    user = User(
        company_id=company.id,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=UserRole.COMPANY_ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
