-- Tabela para armazenar preços dos comissionistas
CREATE TABLE IF NOT EXISTS commissioner_pricing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pricing_type TEXT NOT NULL, -- 'extra', 'group', 'insurance'
    item_key TEXT NOT NULL, -- ex: 'gps', 'A', 'basic'
    season TEXT, -- 'low', 'mid', 'high' (apenas para grupos)
    price REAL NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pricing_type, item_key, season)
);

-- Inserir preços padrão dos extras
INSERT OR IGNORE INTO commissioner_pricing (pricing_type, item_key, price) VALUES
('extra', 'gps', 5.00),
('extra', 'child_seat', 5.00),
('extra', 'booster_seat', 3.00),
('extra', 'airport_fee', 50.00),
('extra', 'insurance', 15.00),
('extra', 'young_driver', 10.00),
('extra', 'senior_driver', 8.00);

-- Inserir preços padrão dos seguros
INSERT OR IGNORE INTO commissioner_pricing (pricing_type, item_key, price) VALUES
('insurance', 'basic', 0.00),
('insurance', 'medium', 10.00),
('insurance', 'premium', 15.00);

-- Inserir preços padrão dos grupos (exemplo para grupo A)
INSERT OR IGNORE INTO commissioner_pricing (pricing_type, item_key, season, price) VALUES
('group', 'A', 'low', 25.00),
('group', 'A', 'mid', 35.00),
('group', 'A', 'high', 50.00);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_pricing_type ON commissioner_pricing(pricing_type);
CREATE INDEX IF NOT EXISTS idx_pricing_item ON commissioner_pricing(item_key);
