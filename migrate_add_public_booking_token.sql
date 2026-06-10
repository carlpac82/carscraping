-- Adicionar campos para link público de reserva por QR code
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS public_token VARCHAR(32) UNIQUE;
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS public_slug VARCHAR(100);

-- Gerar token e slug para comissionistas existentes
UPDATE commissioners
SET
    public_token = LOWER(SUBSTRING(MD5(RANDOM()::TEXT || id::TEXT), 1, 16)),
    public_slug  = LOWER(REGEXP_REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
        name,
        'Á','a'), 'À','a'), 'Â','a'), 'Ã','a'), 'É','e'), 'Ê','e'), 'Í','i'), '[^a-z0-9]+', '-', 'g'))
WHERE public_token IS NULL;

-- Índices para lookup rápido
CREATE INDEX IF NOT EXISTS idx_commissioners_public_token ON commissioners(public_token);
CREATE INDEX IF NOT EXISTS idx_commissioners_public_slug  ON commissioners(public_slug);
