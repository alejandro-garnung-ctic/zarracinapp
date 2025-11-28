CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Configurar zona horaria a Europe/Madrid
SET timezone = 'Europe/Madrid';

CREATE TABLE customer (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    delivery_hours_open TIME NOT NULL,
    delivery_hours_close TIME NOT NULL,
    timezone VARCHAR(64) NOT NULL DEFAULT 'Europe/Madrid',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE shipment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customer(id),
    description VARCHAR(255) NOT NULL,
    planned_delivery_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE delivery_interaction (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shipment_id UUID NOT NULL REFERENCES shipment(id),
    channel VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    response_code VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);