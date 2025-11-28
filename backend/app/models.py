'''
Modelos ORM
    Define las clases de Python (Customer, Shipment, etc.) que representan las tablas de la DB. SQLAlchemy (ORM) permite manipular registros como objetos de Python.
    Usa database.Base para heredar la estructura de la DB. Es usado por main.py para interactuar con los datos.
'''

from sqlalchemy import Column, String, Boolean, Time, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import event
from datetime import datetime
from zoneinfo import ZoneInfo

import uuid

from .database import Base

# Zona horaria por defecto
MADRID_TZ = ZoneInfo("Europe/Madrid")

def get_madrid_now():
    """Retorna el datetime actual en zona horaria Europe/Madrid"""
    return datetime.now(MADRID_TZ)

class Customer(Base):
    __tablename__ = "customer"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    delivery_hours_open = Column(Time, nullable=False)
    delivery_hours_close = Column(Time, nullable=False)
    timezone = Column(String(64), nullable=False, default="Europe/Madrid")
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_madrid_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=get_madrid_now, onupdate=get_madrid_now)

    shipments = relationship("Shipment", back_populates="customer")

@event.listens_for(Customer, 'before_insert', propagate=True)
def set_customer_timestamps(mapper, connection, target):
    """Establece timestamps con timezone Europe/Madrid antes de insertar"""
    now = get_madrid_now()
    if target.created_at is None:
        target.created_at = now
    if target.updated_at is None:
        target.updated_at = now

@event.listens_for(Customer, 'before_update', propagate=True)
def update_customer_timestamp(mapper, connection, target):
    """Actualiza updated_at con timezone Europe/Madrid antes de actualizar"""
    target.updated_at = get_madrid_now()

class Shipment(Base):
    __tablename__ = "shipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False)
    description = Column(String(255), nullable=False)
    planned_delivery_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_madrid_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=get_madrid_now, onupdate=get_madrid_now)

    customer = relationship("Customer", back_populates="shipments")
    interactions = relationship("DeliveryInteraction", back_populates="shipment")

@event.listens_for(Shipment, 'before_insert', propagate=True)
def set_shipment_timestamps(mapper, connection, target):
    """Establece timestamps con timezone Europe/Madrid antes de insertar"""
    now = get_madrid_now()
    if target.created_at is None:
        target.created_at = now
    if target.updated_at is None:
        target.updated_at = now

@event.listens_for(Shipment, 'before_update', propagate=True)
def update_shipment_timestamp(mapper, connection, target):
    """Actualiza updated_at con timezone Europe/Madrid antes de actualizar"""
    target.updated_at = get_madrid_now()

class DeliveryInteraction(Base):
    __tablename__ = "delivery_interaction"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipment.id"), nullable=False)
    channel = Column(String(20), nullable=False)      # whatsapp / sms
    direction = Column(String(10), nullable=False)    # outbound / inbound
    content = Column(String, nullable=False)
    response_code = Column(String(50))
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_madrid_now)

    shipment = relationship("Shipment", back_populates="interactions")

@event.listens_for(DeliveryInteraction, 'before_insert', propagate=True)
def set_interaction_timestamp(mapper, connection, target):
    """Establece timestamp con timezone Europe/Madrid antes de insertar"""
    if target.created_at is None:
        target.created_at = get_madrid_now()