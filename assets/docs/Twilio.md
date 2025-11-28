**Importante para Twilio Sandbox:**
- El número debe estar registrado en el Twilio Sandbox
- Acceder a https://console.twilio.com/us1/develop/sms/sandbox
- Enviar el código de join al número de Twilio desde WhatsApp
- Solo los números registrados pueden recibir mensajes en el Sandbox

**Nota**: Para pruebas, se usa el **Twilio Sandbox**, que es gratuito. Se necesita:
1. Crear cuenta en [Twilio](https://www.twilio.com/)
2. Activar WhatsApp Sandbox (Messaging => Send a WhatsApp message => Sandbox)
3. Enviar el código de activación al número de Twilio desde WhatsApp # En este momento nos dice Twilio Sandbox OK, You are all set! [...]

### Twilio Sandbox vs Número Verificado de WhatsApp

**Twilio Sandbox (Entorno de Pruebas):**
- ✅ Gratuito para pruebas
- ✅ Fácil de configurar
- ❌ Solo envía a números que se unan manualmente al Sandbox
- ❌ No permite botones interactivos
- ❌ Limitado en funcionalidades
- **Uso**: Ideal para PoC y desarrollo

**Número Verificado de WhatsApp Business (Producción):**
- ✅ Envía a cualquier número de WhatsApp
- ✅ Permite botones interactivos (con plantillas aprobadas)
- ✅ Más funcionalidades (plantillas, respuestas rápidas, etc.)
- ❌ Requiere aprobación de Meta/WhatsApp
- ❌ Tiene costos (pago por uso)
- ❌ Proceso de verificación más complejo
- **Uso**: Para producción y uso real

**Nota**: Para pasar a producción, se necesita solicitar un número oficial de WhatsApp Business a través de Twilio y obtener la aprobación de Meta.

### 💰 Costos de Twilio

- **Sandbox**: Gratuito para pruebas (limitado)
- **Producción**: Pago por uso (tarifa por sesión + tarifa por mensaje)
- Consultar [precios de Twilio](https://www.twilio.com/pricing) antes de pasar a producción

## 🔧 Configurar Webhook de Twilio (para DESARROLLADORES)

Para más información, ver [Ngrok.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/Ngrok.md).

### Alternativa: Twilio Functions (No recomendado para PoC)

La URL `https://timberwolf-mastiff-9776.twil.io/demo-reply` es de **Twilio Functions**. Se podría crear una función allí que redirija al servidor, pero es más complejo. Para la PoC, **ngrok es la solución más simple**.

### ¿Qué hace el webhook?

Cuando el cliente responde "SI" o "NO":
- El webhook recibe la respuesta
- Actualiza el estado del shipment en la base de datos
- Envía automáticamente un mensaje de respuesta:
  - **SI** → "Perfecto, hemos confirmado su disponibilidad. Gracias..."
  - **NO** → "Entendido. ¿Podría indicarnos qué horarios le vendrían mejor..."
