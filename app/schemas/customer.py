from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from datetime import datetime


class CustomerBase(BaseModel):
    # Identificación Fiscal
    razon_social: str
    nombre_comercial: Optional[str] = None
    pais: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_fiscal: Optional[str] = None
    regimen_fiscal: Optional[str] = None

    # Ubicación
    region: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    direccion_fiscal: Optional[str] = None
    direccion_despacho: Optional[str] = None

    # Contacto Principal
    telefono_principal: Optional[str] = None
    correo_principal: Optional[EmailStr] = None
    sitio_web: Optional[str] = None

    # Contacto Específico
    contacto_nombre: Optional[str] = None
    contacto_cargo: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_correo: Optional[EmailStr] = None

    # Datos Comerciales
    condicion_pago: Optional[str] = None
    limite_credito: Optional[Decimal] = None
    moneda: Optional[str] = "USD"
    notas: Optional[str] = None
    estatus: Optional[str] = "Activo"


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    razon_social: Optional[str] = None


class CustomerOut(CustomerBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
