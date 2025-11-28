'''
Esquemas de Datos (Pydantic)
    Define cómo deben verse los datos que entran y salen de la API (ej. qué campos tiene un cliente al crearlo). 
    Asegura la validez de los datos.
    Es usado por main.py para validar las peticiones HTTP y estructurar las respuestas.
'''

from datetime import time, datetime
from typing import Optional, Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_serializer


# CUSTOMER

class CustomerBase(BaseModel):
    name: str
    phone: str
    delivery_hours_open: time
    delivery_hours_close: time
    timezone: str = "Europe/Madrid"


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    delivery_hours_open: Optional[time]
    delivery_hours_close: Optional[time]
    timezone: Optional[str]


class CustomerOut(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info):
        """Serializa datetime en formato ISO 8601 con timezone"""
        if dt.tzinfo is None:
            # Si no tiene timezone, asumir Europe/Madrid
            dt = dt.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        return dt.isoformat()

    class Config:
        from_attributes = True


# SHIPMENT

StatusType = Literal["pending", "confirmed", "rejected", "rescheduled", "delivered", "failed"]


class ShipmentBase(BaseModel):
    customer_id: UUID
    description: str
    planned_delivery_time: datetime


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentOut(ShipmentBase):
    id: UUID
    status: StatusType
    created_at: datetime
    updated_at: datetime

    @field_serializer('planned_delivery_time', 'created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info):
        """Serializa datetime en formato ISO 8601 con timezone"""
        if dt.tzinfo is None:
            # Si no tiene timezone, asumir Europe/Madrid
            dt = dt.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        return dt.isoformat()

    class Config:
        from_attributes = True


# INTERACTION (solo lectura en el MVP)

class DeliveryInteractionOut(BaseModel):
    id: UUID
    shipment_id: UUID
    channel: str
    direction: str
    content: str
    response_code: Optional[str]
    created_at: datetime

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info):
        """Serializa datetime en formato ISO 8601 con timezone"""
        if dt.tzinfo is None:
            # Si no tiene timezone, asumir Europe/Madrid
            dt = dt.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        return dt.isoformat()

    class Config:
        from_attributes = True