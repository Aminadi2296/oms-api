import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class UserRole(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    COMPANY_ADMIN = "COMPANY_ADMIN"
    EMPLOYEE = "EMPLOYEE"


class OrderPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


# -------------------------------------------------------------
# 1. Company (Tenant)
# -------------------------------------------------------------
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Límites de suscripción
    subscription_plan = Column(String(50), default="STARTER")  # STARTER, PRO, ENTERPRISE
    max_users = Column(Integer, default=5)                     # Límite de empleados
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan")
    stages = relationship("WorkflowStage", back_populates="company", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="company", cascade="all, delete-orphan")


# -------------------------------------------------------------
# 2. Users (Empleados / Admins)
# -------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True) # Null solo para SUPERADMIN
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    company = relationship("Company", back_populates="users")
    assigned_orders = relationship("Order", back_populates="assigned_to")


# -------------------------------------------------------------
# 3. Customer (Clientes finales - Coincide con tu Frontend MUI)
# -------------------------------------------------------------
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    # Identificación Fiscal
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255), nullable=True)
    pais = Column(String(100), nullable=True)
    tipo_documento = Column(String(50), nullable=True)
    numero_fiscal = Column(String(100), nullable=True)
    regimen_fiscal = Column(String(100), nullable=True)

    # Ubicación
    region = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    codigo_postal = Column(String(50), nullable=True)
    direccion_fiscal = Column(Text, nullable=True)
    direccion_despacho = Column(Text, nullable=True)

    # Contacto Principal (¡Vital para futuros mensajes de WhatsApp!)
    telefono_principal = Column(String(50), nullable=True)
    correo_principal = Column(String(255), nullable=True)
    sitio_web = Column(String(255), nullable=True)

    # Contacto Específico
    contacto_nombre = Column(String(255), nullable=True)
    contacto_cargo = Column(String(100), nullable=True)
    contacto_telefono = Column(String(50), nullable=True)
    contacto_correo = Column(String(255), nullable=True)

    # Datos Comerciales
    condicion_pago = Column(String(100), nullable=True)
    limite_credito = Column(Numeric(12, 2), nullable=True)
    moneda = Column(String(10), default="USD")
    notas = Column(Text, nullable=True)
    estatus = Column(String(50), default="Activo")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    company = relationship("Company", back_populates="customers")
    orders = relationship("Order", back_populates="customer")


# -------------------------------------------------------------
# 4. WorkflowStage (Columnas personalizables del Kanban)
# -------------------------------------------------------------
class WorkflowStage(Base):
    __tablename__ = "workflow_stages"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)        # Ej: "Nuevo", "Diseño", "Producción", "Finalizado"
    position = Column(Integer, default=0)             # Orden visual de izquierda a derecha (0, 1, 2...)
    color = Column(String(20), default="#3b82f6")     # Color para badges o columnas en la UI
    is_completed_stage = Column(Boolean, default=False) # Si es True, llegar aquí marca el pedido como completado

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    company = relationship("Company", back_populates="stages")
    orders = relationship("Order", back_populates="stage")


# -------------------------------------------------------------
# 5. Order (Pedidos / Trabajos en el Kanban)
# -------------------------------------------------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    order_number = Column(String(50), nullable=False, index=True) # Ej: ORD-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Relaciones de estado y asignación
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    stage_id = Column(Integer, ForeignKey("workflow_stages.id", ondelete="RESTRICT"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Prioridad y Fechas
    priority = Column(Enum(OrderPriority), default=OrderPriority.MEDIUM, nullable=False)
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Posición dentro de la columna para drag-and-drop
    position = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    company = relationship("Company", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    stage = relationship("WorkflowStage", back_populates="orders")
    assigned_to = relationship("User", back_populates="assigned_orders")
    notes = relationship("OrderNote", back_populates="order", cascade="all, delete-orphan")


# -------------------------------------------------------------
# 6. OrderNote (Notas y comentarios dentro del pedido)
# -------------------------------------------------------------
class OrderNote(Base):
    __tablename__ = "order_notes"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="notes")
    author = relationship("User")
