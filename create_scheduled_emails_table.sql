-- Tabela para agendar emails de self-checkout
CREATE TABLE IF NOT EXISTS scheduled_checkout_emails (
    id SERIAL PRIMARY KEY,
    inspection_number VARCHAR(100) NOT NULL UNIQUE,
    checkout_date DATE NOT NULL,
    scheduled_send_date TIMESTAMP NOT NULL,
    pickup_location VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    client_name VARCHAR(255),
    vehicle_plate VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    error_message TEXT,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'sent', 'cancelled', 'error'))
);

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_scheduled_emails_send_date ON scheduled_checkout_emails(scheduled_send_date);
CREATE INDEX IF NOT EXISTS idx_scheduled_emails_status ON scheduled_checkout_emails(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_emails_inspection ON scheduled_checkout_emails(inspection_number);

-- Comentários
COMMENT ON TABLE scheduled_checkout_emails IS 'Agendamento automático de emails de self-checkout 2 dias antes da data de checkout (apenas Aeroporto de Faro)';
COMMENT ON COLUMN scheduled_checkout_emails.status IS 'pending: aguardando envio | sent: enviado com sucesso | cancelled: cancelado (data alterada) | error: erro no envio';
