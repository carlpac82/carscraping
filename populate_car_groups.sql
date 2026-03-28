-- Popular tabela car_groups com os 14 grupos de veículos
-- Se a tabela não existir, criar primeiro

CREATE TABLE IF NOT EXISTS car_groups (
    code VARCHAR(10) PRIMARY KEY,
    brand VARCHAR(100),
    model VARCHAR(100),
    photo_url TEXT,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Limpar dados existentes
DELETE FROM car_groups;

-- Inserir os 14 grupos de veículos
INSERT INTO car_groups (code, brand, model, photo_url, enabled) VALUES
('A', 'KIA', 'PICANTO', '', 1),
('B', 'FIAT', 'PANDA', '', 1),
('B1', 'FIAT', 'PANDA', '', 1),
('B2', 'FIAT', 'PANDA', '', 1),
('D', 'SEAT', 'IBIZA', '', 1),
('E1', 'HYUNDAI', 'i10', '', 1),
('E2', 'CITROEN', 'C3', '', 1),
('F', 'SEAT', 'ARONA', '', 1),
('G', 'FIAT', '500 CABRIO', '', 1),
('J1', 'PEUGEOT', '2008', '', 1),
('J2', 'PEUGEOT', '308 SW', '', 1),
('L1', 'CITROEN', 'C3 AIRCROSS', '', 1),
('L2', 'PEUGEOT', '308 SW', '', 1),
('M1', 'DACIA', 'JOGGER', '', 1),
('M2', 'CITROEN', 'C4 PICASSO', '', 1),
('N', 'TOYOTA', 'PROACE', '', 1);

-- Verificar inserção
SELECT code, brand, model, enabled FROM car_groups ORDER BY code;
