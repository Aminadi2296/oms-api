from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from pydantic.alias_generators import to_camel
from datetime import datetime


class CustomerBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
    )

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
    correo_principal: Optional[str] = None  # String flexible para evitar rechazo si está vacío
    sitio_web: Optional[str] = None

    # Contacto Específico
    contacto_nombre: Optional[str] = None
    contacto_cargo: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_correo: Optional[str] = None

    # Datos Comerciales
    condicion_pago: Optional[str] = None
    limite_credito: Optional[Decimal] = None
    moneda: Optional[str] = "USD"
    notas: Optional[str] = None
    estatus: Optional[str] = "Activo"

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    razon_social: Optional[str] = None


class CustomerOut(CustomerBase):
    id: int
    company_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
