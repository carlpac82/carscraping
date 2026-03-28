-- Verificar estado da tabela car_groups
SELECT 
    code, 
    brand, 
    model, 
    enabled,
    photo_url,
    pg_typeof(enabled) as tipo_enabled
FROM car_groups 
ORDER BY code;

-- Contar registos
SELECT COUNT(*) as total_grupos FROM car_groups;

-- Contar registos com enabled = 1
SELECT COUNT(*) as grupos_enabled FROM car_groups WHERE enabled = 1;
