# 🚚 PoC Sistema de Notificación de Entregas - Zarracina

Sistema de prueba de concepto (PoC) para automatizar la confirmación de entregas mediante WhatsApp usando Twilio.

## 📋 Resumen del Proyecto

Este sistema permite:
- **Registrar clientes** (bares, minoristas) con sus datos de contacto
- **Crear envíos** que automáticamente envían un mensaje de WhatsApp al cliente
- **Recibir respuestas** del cliente ("SI"/"NO") y actualizar el estado del envío en tiempo real
- **Visualizar el estado** de todos los envíos desde un dashboard simple

### Flujo Principal

1. Planifican los envíos deseados desde la Google Spreadsheet [Programación de pedidos](https://docs.google.com/spreadsheets/d/contacta-con-el-dueño-del-repo) (contacta con el dueño del repo para acceder a esta).
2. Levanta el sistema si no está ya en funcionamiento. Ver [Init.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/Init.md).
3. Si no lo estás, date de alta en Twilio Sandbox, ver [Twilio](https://github.com/alejandro-garnung-ctic/zarracinapp?tab=readme-ov-file#twilio).
4. Accede al [dashboard](https://github.com/alejandro-garnung-ctic/zarracinapp?tab=readme-ov-file#dashboard) y pulsa el botón `📝 Procesar pedidos` para lanzar las órdenes que programaste en la Google Spreadsheet.
5. En este momento, el sistema envía automáticamente un WhatsApp a cada orden planificada: *"Estimado NOMBRE_CLIENTE, iremos hoy a las XX:XX. ¿Puedes? Responde con SI o NO."*
6. Espera a dicho mensaje, viendo el dashboard en tiempo real, y cuando llegue, responde.
7. El sistema actualiza el estado del envío:
   - **SI** → `confirmed` (verde) → el sistema responde con un mensaje de confirmación.
   - **NO** → `rejected` (rojo) → el sistema pregunta por qué horas dispone el cliente.

#### Próximos pasos: 

 - Manejar qué horas dispone y propone el cliente.
 - Usar un número de Whatsapp Bussiness verificado en vez del entorno de pruebas Twilio Sandbox.

El **Dashboard web** de la PoC está accesible en `https://zarracina-delivery.test.ctic.es/dashboard`.

## Twilio

En esta POC se utiliza Twilio Sandbox para enviar y recibir mensajes por Whatsapp, de manera gratuita. 

Los contactos que deseen utilizar la herramienta deben darse de alta en el sistema:

1. Para darte de alta, envía por Whatsapp el mensaje `join later-ice` al siguiente número: `+14155238886`.

Una vez dado de alta ya podrías recibir mensajes del bot y posteriormente contestarlos. 

Para más información, ver [Twilio.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/Twilio.md).

## 📊 Dashboard

Accede al dashboard en: **https://zarracina-delivery.test.ctic.es/dashboard**

El dashboard es una interfaz web simple y minimalista que permite visualizar el estado del sistema en tiempo real.

Para más información, ver [Dashboard.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/Dashboard.md).

## 📝 Uso de la API (para DESARROLLADORES)

Para más información, ver [API.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/API.md).

## 💾 Base de datos (para DESARROLLADORES)

Para más información, ver [BBDD.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/BBDD.md).

## Más información

Al ser una Prueba de Concepto, muchos aspecto se tratan superficialmente, pues el objetivo es mostrar la potencial funcionalidad de la aplicación. 

Para más información, ver [Info.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/Info.md).

## 🐛 Troubleshooting

Para más información, ver [Troubleshooting.md](https://github.com/alejandro-garnung-ctic/zarracinapp/blob/main/assets/docs/Troubleshooting.md).

