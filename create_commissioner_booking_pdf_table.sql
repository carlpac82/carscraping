-- Tabela para armazenar coordenadas do PDF Livro de Reservas dos Comissionistas
-- Similar ao sistema de rental_agreement_coordinates

CREATE TABLE IF NOT EXISTS commissioner_booking_coordinates (
    id SERIAL PRIMARY KEY,
    field_id TEXT NOT NULL UNIQUE,
    x REAL NOT NULL,
    y REAL NOT NULL,
    width REAL,
    height REAL,
    page INTEGER DEFAULT 1,
    field_type TEXT DEFAULT 'text',
    template_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca rápida por field_id
CREATE INDEX IF NOT EXISTS idx_commissioner_booking_coords_field 
ON commissioner_booking_coordinates(field_id);

-- Índice para busca por página
CREATE INDEX IF NOT EXISTS idx_commissioner_booking_coords_page 
ON commissioner_booking_coordinates(page);

-- Comentários sobre os campos
COMMENT ON TABLE commissioner_booking_coordinates IS 'Coordenadas para mapeamento de campos no PDF Livro de Reservas dos Comissionistas';
COMMENT ON COLUMN commissioner_booking_coordinates.field_id IS 'Identificador único do campo (ex: voucher_number, client_name, pickup_date)';
COMMENT ON COLUMN commissioner_booking_coordinates.x IS 'Coordenada X (horizontal) do campo no PDF';
COMMENT ON COLUMN commissioner_booking_coordinates.y IS 'Coordenada Y (vertical) do campo no PDF';
COMMENT ON COLUMN commissioner_booking_coordinates.width IS 'Largura do campo';
COMMENT ON COLUMN commissioner_booking_coordinates.height IS 'Altura do campo';
COMMENT ON COLUMN commissioner_booking_coordinates.page IS 'Número da página do PDF (1-indexed)';
COMMENT ON COLUMN commissioner_booking_coordinates.field_type IS 'Tipo do campo: text, date, number, etc';
COMMENT ON COLUMN commissioner_booking_coordinates.template_version IS 'Versão do template PDF';

-- Lista de campos esperados (baseado nos dados da reserva dos comissionistas):
-- voucher_number - Número do voucher
-- client_name - Nome do cliente
-- client_email - Email do cliente
-- client_phone - Telefone do cliente
-- client_hotel - Hotel do cliente
-- client_room - Número do quarto
-- pickup_date - Data de levantamento
-- pickup_time - Hora de levantamento
-- pickup_location - Local de levantamento
-- dropoff_date - Data de entrega
-- dropoff_time - Hora de entrega
-- dropoff_location - Local de entrega
-- vehicle_group - Grupo do veículo
-- vehicle_name - Nome do veículo
-- flight_number - Número do voo
-- observations - Observações
-- total_price - Preço total
-- base_price - Preço base
-- insurance_price - Preço do seguro
-- road_tax - Road tax
-- extras - Extras (GPS, cadeira, etc)
-- commissioner_name - Nome do comissionista
-- created_date - Data de criação da reserva
