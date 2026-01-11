-- Remove constraints NOT NULL
ALTER TABLE "automated_price_rules" ALTER COLUMN "strategy_type" DROP NOT NULL;
ALTER TABLE "automated_price_rules" ALTER COLUMN "priority" DROP NOT NULL;
ALTER TABLE "automated_price_rules" ALTER COLUMN "created_at" DROP NOT NULL;

-- Limpar tabelas
TRUNCATE TABLE "automated_price_rules" CASCADE;
TRUNCATE TABLE "oauth_tokens" CASCADE;
