-- ============================================================================
-- PERFORMANCE OPTIMIZATION: DATABASE INDEXES
-- ============================================================================
-- Este script cria índices para melhorar a performance das queries
-- SEGURO: Não altera dados, apenas adiciona "atalhos" para queries mais rápidas
-- Ganho esperado: 50-80% mais rápido em queries com JOIN e filtros
-- ============================================================================

-- 1. ÍNDICES EM FOREIGN KEYS (para JOINs mais rápidos)
-- ============================================================================

-- Commission Bookings
CREATE INDEX IF NOT EXISTS idx_commission_bookings_commissioner_id 
  ON commission_bookings(commissioner_id);

CREATE INDEX IF NOT EXISTS idx_commission_bookings_pickup_date 
  ON commission_bookings(pickup_date);

CREATE INDEX IF NOT EXISTS idx_commission_bookings_commission_paid 
  ON commission_bookings(commission_paid);

CREATE INDEX IF NOT EXISTS idx_commission_bookings_created_at 
  ON commission_bookings(created_at);

-- Rental Agreements
CREATE INDEX IF NOT EXISTS idx_rental_agreements_vehicle_id 
  ON rental_agreements(vehicle_id);

CREATE INDEX IF NOT EXISTS idx_rental_agreements_created_at 
  ON rental_agreements(created_at);

-- Vehicle Inspections
CREATE INDEX IF NOT EXISTS idx_vehicle_inspections_rental_agreement 
  ON vehicle_inspections(rental_agreement);

CREATE INDEX IF NOT EXISTS idx_vehicle_inspections_inspection_type 
  ON vehicle_inspections(inspection_type);

CREATE INDEX IF NOT EXISTS idx_vehicle_inspections_created_at 
  ON vehicle_inspections(created_at);

-- Damage Reports
CREATE INDEX IF NOT EXISTS idx_damage_reports_dr_number 
  ON damage_reports(dr_number);

CREATE INDEX IF NOT EXISTS idx_damage_reports_rental_agreement 
  ON damage_reports(rental_agreement);

CREATE INDEX IF NOT EXISTS idx_damage_reports_created_at 
  ON damage_reports(created_at);

-- 2. ÍNDICES COMPOSTOS (para queries com múltiplos filtros)
-- ============================================================================

-- Commission Bookings: filtro por commissioner + data
CREATE INDEX IF NOT EXISTS idx_commission_bookings_commissioner_pickup 
  ON commission_bookings(commissioner_id, pickup_date DESC);

-- Commission Bookings: filtro por paid status + data
CREATE INDEX IF NOT EXISTS idx_commission_bookings_paid_pickup 
  ON commission_bookings(commission_paid, pickup_date DESC);

-- Vehicle Inspections: filtro por RA + tipo
CREATE INDEX IF NOT EXISTS idx_vehicle_inspections_ra_type 
  ON vehicle_inspections(rental_agreement, inspection_type);

-- 3. ÍNDICES PARA PESQUISAS DE TEXTO (ILIKE queries)
-- ============================================================================

-- Commissioners: pesquisa por nome
CREATE INDEX IF NOT EXISTS idx_commissioners_name_lower 
  ON commissioners(LOWER(name));

-- Vehicles: pesquisa por matrícula
CREATE INDEX IF NOT EXISTS idx_vehicles_license_plate_lower 
  ON vehicles(LOWER(license_plate));

-- Rental Agreements: pesquisa por RA number
CREATE INDEX IF NOT EXISTS idx_rental_agreements_ra_number_lower 
  ON rental_agreements(LOWER(rental_agreement_number));

-- ============================================================================
-- ANÁLISE DE PERFORMANCE (opcional - para verificar ganhos)
-- ============================================================================

-- Para ver estatísticas de uso dos índices:
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- ORDER BY idx_scan DESC;

-- Para ver tamanho dos índices:
-- SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid))
-- FROM pg_stat_user_indexes
-- ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================================================
-- FIM DO SCRIPT
-- ============================================================================
