import enum
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


def to_naive_utc(value: datetime | None) -> datetime | None:
    """La BD guarda UTC sin zona horaria (TIMESTAMP WITHOUT TIME ZONE)."""
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


class OrderPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class OrderBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
        str_strip_whitespace=True,
    )

    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    customer_id: int
    stage_id: int
    assigned_to_id: Optional[int] = None
    priority: OrderPriority = OrderPriority.MEDIUM
    deadline: Optional[datetime] = None
    position: int = 0


class OrderCreate(OrderBase):
    @field_validator("deadline", mode="after")
    @classmethod
    def normalize_deadline(cls, value: datetime | None) -> datetime | None:
        return to_naive_utc(value)


class OrderUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
        str_strip_whitespace=True,
    )

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    customer_id: Optional[int] = None
    stage_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    priority: Optional[OrderPriority] = None
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    position: Optional[int] = None

    @field_validator("deadline", "completed_at", mode="after")
    @classmethod
    def normalize_datetimes(cls, value: datetime | None) -> datetime | None:
        return to_naive_utc(value)


class OrderOut(OrderBase):
    id: int
    company_id: int
    order_number: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None