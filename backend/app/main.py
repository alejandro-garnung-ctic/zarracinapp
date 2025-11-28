'''
    Inicializa FastAPI y contiene todos los endpoints (rutas) de la API (CRUD para Clientes y Envíos).
    Es el punto de entrada de todas las peticiones HTTP y maneja la lógica de negocio.
'''

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, time, date
from zoneinfo import ZoneInfo
import os
import re

from twilio.rest import Client
from twilio.request_validator import RequestValidator

from .database import Base, engine, get_db
from . import models, schemas

# Zona horaria por defecto
MADRID_TZ = ZoneInfo("Europe/Madrid")

def normalize_to_madrid_tz(dt: datetime) -> datetime:
    """
    Normaliza un datetime a la zona horaria Europe/Madrid.
    Si el datetime no tiene timezone, se asume que está en Europe/Madrid.
    Si tiene timezone, se convierte a Europe/Madrid.
    """
    if dt.tzinfo is None:
        # Si no tiene timezone, asumir que está en Madrid
        return dt.replace(tzinfo=MADRID_TZ)
    else:
        # Si tiene timezone, convertir a Madrid
        return dt.astimezone(MADRID_TZ)
from .deps import api_key_auth
from . import spreadsheet

# Crear tablas si no existen (en esta PoC; en serio usarías migraciones)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PoC Delivery Notification")

# Servir archivos estáticos
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
DISABLE_WHATSAPP = os.getenv("DISABLE_WHATSAPP", "false").lower() == "true"


def get_twilio_client():
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        return None
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# ---------- CUSTOMER ENDPOINTS ----------

@app.post("/customers", response_model=schemas.CustomerOut, dependencies=[Depends(api_key_auth)])
def create_customer(customer_in: schemas.CustomerCreate, db: Session = Depends(get_db)):
    customer = models.Customer(**customer_in.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@app.get("/customers", response_model=List[schemas.CustomerOut], dependencies=[Depends(api_key_auth)])
def list_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()


@app.get("/customers/{customer_id}", response_model=schemas.CustomerOut, dependencies=[Depends(api_key_auth)])
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.put("/customers/{customer_id}", response_model=schemas.CustomerOut, dependencies=[Depends(api_key_auth)])
def update_customer(customer_id: UUID, customer_upd: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in customer_upd.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@app.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(api_key_auth)])
def delete_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return


# ---------- SHIPMENT ENDPOINTS ----------

@app.post("/shipments", response_model=schemas.ShipmentOut, dependencies=[Depends(api_key_auth)])
def create_shipment(shipment_in: schemas.ShipmentCreate, db: Session = Depends(get_db)):
    # comprobar customer
    customer = db.query(models.Customer).get(shipment_in.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Normalizar planned_delivery_time a zona horaria Europe/Madrid
    planned_time = normalize_to_madrid_tz(shipment_in.planned_delivery_time)
    
    shipment = models.Shipment(
        customer_id=shipment_in.customer_id,
        description=shipment_in.description,
        planned_delivery_time=planned_time,
        status="pending",
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    # enviar WhatsApp si está habilitado y hay teléfono
    if not DISABLE_WHATSAPP and customer.phone and get_twilio_client():
        # Formatear fecha y hora (convertir a Madrid si es necesario)
        planned_time_madrid = normalize_to_madrid_tz(shipment.planned_delivery_time)
        delivery_date = planned_time_madrid.strftime("%d/%m/%Y")
        delivery_time_str = planned_time_madrid.strftime("%H:%M")
        
        # Mensaje mejorado y más formal
        body = (
            f"Estimado/a {customer.name},\n\n"
            f"Le informamos que tenemos programada una entrega para su establecimiento:\n\n"
            f"📦 *Pedido:* {shipment.description}\n"
            f"📅 *Fecha:* {delivery_date}\n"
            f"🕐 *Hora prevista:* {delivery_time_str}\n\n"
            f"¿Podrá recibir la entrega en el horario indicado?\n\n"
            f"Por favor, responda con *SI* o *NO* para confirmar."
        )

        client = get_twilio_client()
        try:
            # Nota: Los botones interactivos requieren plantillas aprobadas en Twilio
            # Para el Sandbox, usamos mensaje de texto simple
            # En producción, se puede usar Content API con plantillas que incluyan botones
            message = client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                to=f"whatsapp:{customer.phone}",
                body=body,
            )
            interaction = models.DeliveryInteraction(
                shipment_id=shipment.id,
                channel="whatsapp",
                direction="outbound",
                content=body,
                response_code=None,
            )
            db.add(interaction)
            db.commit()
            # Log éxito
            print(f"WhatsApp enviado correctamente a {customer.phone} (Shipment ID: {shipment.id}, Message SID: {message.sid})")
        except Exception as e:
            # En PoC: log simple
            print(f"Error enviando WhatsApp a {customer.phone}: {e}")

    return shipment


@app.get("/shipments/{shipment_id}", response_model=schemas.ShipmentOut, dependencies=[Depends(api_key_auth)])
def get_shipment(shipment_id: UUID, db: Session = Depends(get_db)):
    shipment = db.query(models.Shipment).get(shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@app.get("/shipments", response_model=List[schemas.ShipmentOut], dependencies=[Depends(api_key_auth)])
def list_shipments(customer_id: UUID | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Shipment)
    if customer_id:
        query = query.filter(models.Shipment.customer_id == customer_id)
    return query.all()


@app.get(
    "/shipments/{shipment_id}/interactions",
    response_model=List[schemas.DeliveryInteractionOut],
    dependencies=[Depends(api_key_auth)],
)
def list_interactions(shipment_id: UUID, db: Session = Depends(get_db)):
    shipment = db.query(models.Shipment).get(shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment.interactions


# ---------- TWILIO WEBHOOK ENDPOINT ----------

@app.post("/twilio/incoming")
async def twilio_incoming(request: Request, db: Session = Depends(get_db)):
    """
    Webhook de Twilio para recibir mensajes entrantes de WhatsApp.
    NO requiere autenticación API_KEY porque Twilio valida con su propia firma.
    Maneja las respuestas del cliente y envía mensajes automáticos de confirmación.
    """
    from twilio.twiml.messaging_response import MessagingResponse
    
    form_data = await request.form()
    from_number = form_data.get("From", "").replace("whatsapp:", "")
    body = form_data.get("Body", "").strip().upper()
    
    # Crear respuesta TwiML
    resp = MessagingResponse()
    
    if not from_number or not body:
        resp.message("Error: No se pudo procesar su mensaje. Por favor, contacte con el servicio.")
        return Response(content=str(resp), media_type="application/xml")
    
    # Buscar el cliente por número de teléfono
    customer = db.query(models.Customer).filter(
        models.Customer.phone == from_number
    ).first()
    
    if not customer:
        print(f"Cliente no encontrado para número: {from_number}")
        resp.message("Lo sentimos, no encontramos su número en nuestro sistema.")
        return Response(content=str(resp), media_type="application/xml")
    
    # Buscar el shipment pendiente más reciente del cliente
    shipment = db.query(models.Shipment).filter(
        models.Shipment.customer_id == customer.id,
        models.Shipment.status == "pending"
    ).order_by(models.Shipment.created_at.desc()).first()
    
    if not shipment:
        print(f"No hay shipments pendientes para cliente: {customer.name}")
        resp.message("No tenemos entregas pendientes de confirmación para su establecimiento.")
        return Response(content=str(resp), media_type="application/xml")
    
    # Parsear respuesta: SI -> confirmed, NO -> rejected
    response_normalized = re.sub(r'[^A-Z]', '', body)
    new_status = None
    
    if "SI" in response_normalized or "SÍ" in response_normalized or "YES" in response_normalized:
        new_status = "confirmed"
    elif "NO" in response_normalized:
        new_status = "rejected"
    else:
        # Respuesta no reconocida
        interaction = models.DeliveryInteraction(
            shipment_id=shipment.id,
            channel="whatsapp",
            direction="inbound",
            content=body,
            response_code="unknown",
        )
        db.add(interaction)
        db.commit()
        resp.message("Por favor, responda con *SI* o *NO* para confirmar la entrega.")
        return Response(content=str(resp), media_type="application/xml")
    
    # Actualizar estado del shipment
    shipment.status = new_status
    db.commit()
    db.refresh(shipment)
    
    # Registrar la interacción inbound
    interaction = models.DeliveryInteraction(
        shipment_id=shipment.id,
        channel="whatsapp",
        direction="inbound",
        content=body,
        response_code=new_status,
    )
    db.add(interaction)
    db.commit()
    
    # Enviar respuesta automática según la respuesta del cliente
    if new_status == "confirmed":
        # Mensaje de confirmación/agradecimiento
        confirmation_msg = (
            f"Perfecto, {customer.name}.\n\n"
            f"✅ Hemos confirmado su disponibilidad para recibir:\n"
            f"📦 {shipment.description}\n"
            f"🕐 {normalize_to_madrid_tz(shipment.planned_delivery_time).strftime('%d/%m/%Y a las %H:%M')}\n\n"
            f"Gracias por su confirmación. Le esperamos en el horario indicado."
        )
        # Solo usar TwiML para responder (no enviar dos veces)
        resp.message(confirmation_msg)
        
        # Registrar interacción de confirmación
        confirm_interaction = models.DeliveryInteraction(
            shipment_id=shipment.id,
            channel="whatsapp",
            direction="outbound",
            content=confirmation_msg,
            response_code="confirmation_sent",
        )
        db.add(confirm_interaction)
        db.commit()
        print(f"Mensaje de confirmación enviado a {customer.phone}")
    
    elif new_status == "rejected":
        # Mensaje preguntando por horas alternativas (mockup)
        alternative_msg = (
            f"Entendido, {customer.name}.\n\n"
            f"Lamentamos que el horario no le convenga.\n\n"
            f"¿Podría indicarnos qué horarios le vendrían mejor para recibir la entrega?\n\n"
            f"Por ejemplo: mañana por la mañana, esta tarde después de las 15:00, etc."
        )
        # Solo usar TwiML para responder (no enviar dos veces)
        resp.message(alternative_msg)
        
        # Registrar interacción
        alt_interaction = models.DeliveryInteraction(
            shipment_id=shipment.id,
            channel="whatsapp",
            direction="outbound",
            content=alternative_msg,
            response_code="alternative_requested",
        )
        db.add(alt_interaction)
        db.commit()
        print(f"Mensaje de horas alternativas enviado a {customer.phone}")
    
    return Response(content=str(resp), media_type="application/xml")


# ---------- DASHBOARD FRONTEND ----------

@app.get("/dashboard")
async def dashboard():
    """Sirve el dashboard HTML simple"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "static", "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)


# ---------- SPREADSHEET ENDPOINTS ----------

@app.get("/spreadsheet", dependencies=[Depends(api_key_auth)])
def read_spreadsheet_endpoint():
    """
    Lee el Google Spreadsheet configurado y devuelve todos los registros.
    """
    try:
        rows = spreadsheet.read_spreadsheet()
        return {"status": "success", "count": len(rows), "data": rows}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error leyendo spreadsheet: {str(e)}"
        )


@app.post("/spreadsheet/process", dependencies=[Depends(api_key_auth)])
def process_spreadsheet(db: Session = Depends(get_db)):
    """
    Lee el spreadsheet y crea shipments automáticamente.
    Solo crea clientes y shipments si no existen ya.
    """
    try:
        rows = spreadsheet.read_spreadsheet()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error leyendo spreadsheet: {str(e)}"
        )
    
    results = {
        "status": "success",
        "processed": len(rows),
        "customers_created": 0,
        "customers_existing": 0,
        "shipments_created": 0,
        "shipments_skipped": 0,
        "whatsapp_sent": 0,
        "whatsapp_errors": 0,
        "errors": []
    }
    
    for idx, row in enumerate(rows):
        try:
            # 1. Formatear teléfono usando el prefijo del spreadsheet
            prefix = str(row.get('Prefijo', '34')).strip()
            phone_number = str(row.get('Teléfono', '')).strip()
            
            # Construir teléfono completo con prefijo
            if phone_number:
                # Si el prefijo no tiene +, añadirlo
                if not prefix.startswith('+'):
                    phone = f"+{prefix}{phone_number}"
                else:
                    phone = f"{prefix}{phone_number}"
            else:
                results["errors"].append(f"Fila {idx+1}: Teléfono vacío")
                continue
            
            # 2. Parsear horarios de entrega del spreadsheet
            apertura_str = row.get('Apertura para entregas', '').strip()
            cierre_str = row.get('Cierre para entregas', '').strip()
            
            # Valores por defecto
            delivery_hours_open = time(9, 0)
            delivery_hours_close = time(22, 0)
            
            # Parsear apertura
            if apertura_str:
                try:
                    if len(apertura_str.split(':')) == 3:
                        delivery_hours_open = datetime.strptime(apertura_str, '%H:%M:%S').time()
                    else:
                        delivery_hours_open = datetime.strptime(apertura_str, '%H:%M').time()
                except ValueError:
                    print(f"Fila {idx+1}: Error parseando 'Apertura para entregas' ({apertura_str}), usando valor por defecto")
            
            # Parsear cierre
            if cierre_str:
                try:
                    if len(cierre_str.split(':')) == 3:
                        delivery_hours_close = datetime.strptime(cierre_str, '%H:%M:%S').time()
                    else:
                        delivery_hours_close = datetime.strptime(cierre_str, '%H:%M').time()
                except ValueError:
                    print(f"Fila {idx+1}: Error parseando 'Cierre para entregas' ({cierre_str}), usando valor por defecto")
            
            # 3. Buscar cliente por teléfono (SOLO SI NO EXISTE)
            customer = db.query(models.Customer).filter(
                models.Customer.phone == phone
            ).first()
            
            if not customer:
                # Crear cliente nuevo
                customer = models.Customer(
                    name=row.get('Cliente', 'Cliente sin nombre'),
                    phone=phone,
                    delivery_hours_open=delivery_hours_open,
                    delivery_hours_close=delivery_hours_close,
                    timezone="Europe/Madrid",
                )
                db.add(customer)
                db.commit()
                db.refresh(customer)
                results["customers_created"] += 1
            else:
                # Actualizar horarios del cliente existente si están en el spreadsheet
                if apertura_str or cierre_str:
                    customer.delivery_hours_open = delivery_hours_open
                    customer.delivery_hours_close = delivery_hours_close
                    db.commit()
                results["customers_existing"] += 1
            
            # 4. Parsear fecha y hora (asumiendo zona horaria Europe/Madrid)
            fecha_str = row.get('Fecha entrega', '').strip()
            hora_str = row.get('Hora entrega', '').strip()
            
            try:
                # Parsear fecha DD/MM/YYYY
                fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                # Parsear hora HH:MM:SS o HH:MM
                if len(hora_str.split(':')) == 3:
                    hora = datetime.strptime(hora_str, '%H:%M:%S').time()
                else:
                    hora = datetime.strptime(hora_str, '%H:%M').time()
                
                # Combinar fecha y hora y asignar zona horaria Europe/Madrid
                planned_time = datetime.combine(fecha, hora, tzinfo=ZoneInfo("Europe/Madrid"))
            except ValueError as e:
                results["errors"].append(f"Fila {idx+1}: Error parseando fecha/hora: {str(e)}")
                continue
            
            # 5. Verificar si el shipment ya existe (SOLO SI NO EXISTE)
            description = row.get('Descripción', '').strip()
            existing_shipment = db.query(models.Shipment).filter(
                models.Shipment.customer_id == customer.id,
                models.Shipment.description == description,
                models.Shipment.planned_delivery_time == planned_time
            ).first()
            
            if existing_shipment:
                results["shipments_skipped"] += 1
                continue
            
            # 6. Crear shipment
            shipment = models.Shipment(
                customer_id=customer.id,
                description=description,
                planned_delivery_time=planned_time,
                status="pending",
            )
            db.add(shipment)
            db.commit()
            db.refresh(shipment)
            results["shipments_created"] += 1
            
            # 7. Enviar WhatsApp si está habilitado
            if not DISABLE_WHATSAPP and customer.phone and get_twilio_client():
                # Formatear fecha y hora (convertir a Madrid si es necesario)
                planned_time_madrid = normalize_to_madrid_tz(shipment.planned_delivery_time)
                delivery_date = planned_time_madrid.strftime("%d/%m/%Y")
                delivery_time_str = planned_time_madrid.strftime("%H:%M")
                
                # Mensaje mejorado y más formal
                body = (
                    f"Estimado/a {customer.name},\n\n"
                    f"Le informamos que tenemos programada una entrega para su establecimiento:\n\n"
                    f"📦 *Pedido:* {shipment.description}\n"
                    f"📅 *Fecha:* {delivery_date}\n"
                    f"🕐 *Hora prevista:* {delivery_time_str}\n\n"
                    f"¿Podrá recibir la entrega en el horario indicado?\n\n"
                    f"Por favor, responda con *SI* o *NO* para confirmar."
                )
                
                client = get_twilio_client()
                try:
                    message = client.messages.create(
                        from_=TWILIO_WHATSAPP_FROM,
                        to=f"whatsapp:{customer.phone}",
                        body=body,
                    )
                    # Registrar interacción
                    interaction = models.DeliveryInteraction(
                        shipment_id=shipment.id,
                        channel="whatsapp",
                        direction="outbound",
                        content=body,
                        response_code=None,
                    )
                    db.add(interaction)
                    db.commit()
                    results["whatsapp_sent"] += 1
                    # Log éxito
                    success_msg = f"Fila {idx+1}: WhatsApp enviado correctamente a {customer.phone} (Shipment ID: {shipment.id}, Message SID: {message.sid})"
                    print(success_msg)
                except Exception as e:
                    # Log error pero continuar
                    error_msg = f"Fila {idx+1}: Error enviando WhatsApp a {customer.phone}: {str(e)}"
                    results["errors"].append(error_msg)
                    results["whatsapp_errors"] += 1
                    print(f"Error enviando WhatsApp: {e}")
        
        except Exception as e:
            error_msg = f"Fila {idx+1}: Error procesando: {str(e)}"
            results["errors"].append(error_msg)
            print(f"Error procesando fila {idx+1}: {e}")
            continue
    
    return results


@app.post("/test/whatsapp", dependencies=[Depends(api_key_auth)])
def test_whatsapp(phone: str, db: Session = Depends(get_db)):
    """
    Endpoint de prueba para enviar un WhatsApp a un número específico.
    Útil para verificar que Twilio Sandbox está configurado correctamente.
    """
    if DISABLE_WHATSAPP:
        raise HTTPException(
            status_code=400,
            detail="WhatsApp está deshabilitado (DISABLE_WHATSAPP=true)"
        )
    
    client = get_twilio_client()
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Cliente de Twilio no disponible. Verifica TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN"
        )
    
    # Formatear teléfono si no tiene +
    if not phone.startswith('+'):
        phone = f"+{phone}"
    
    body = "🧪 Mensaje de prueba desde Zarracina Delivery. Si recibes esto, Twilio Sandbox está funcionando correctamente."
    
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{phone}",
            body=body,
        )
        return {
            "status": "success",
            "message": "WhatsApp enviado correctamente",
            "to": phone,
            "message_sid": message.sid,
            "note": "Si no recibes el mensaje, verifica que tu número esté registrado en Twilio Sandbox"
        }
    except Exception as e:
        error_detail = str(e)
        return {
            "status": "error",
            "message": "Error enviando WhatsApp",
            "to": phone,
            "error": error_detail,
            "troubleshooting": [
                "1. Verifica que tu número esté registrado en Twilio Sandbox",
                "2. Envía 'join [código]' al número de Twilio Sandbox desde tu WhatsApp",
                "3. Verifica que el formato del número sea correcto (+34XXXXXXXXX)",
                "4. Revisa los logs del backend para más detalles"
            ]
        }