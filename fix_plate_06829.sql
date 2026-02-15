-- Fix plate for RA 06829: BA-28-FP -> BI-78-FM

-- Check current data
SELECT 'BEFORE UPDATE - Inspections:' as info;
SELECT inspection_number, vehicle_plate, contract_number, inspection_type 
FROM vehicle_inspections 
WHERE contract_number LIKE '06829%' AND vehicle_plate = 'BA-28-FP';

SELECT 'BEFORE UPDATE - Rental Agreement:' as info;
SELECT rental_agreement_number, license_plate 
FROM rental_agreements 
WHERE rental_agreement_number LIKE '06829%';

-- Update inspections
UPDATE vehicle_inspections 
SET vehicle_plate = 'BI-78-FM' 
WHERE contract_number LIKE '06829%' AND vehicle_plate = 'BA-28-FP';

-- Update rental agreement
UPDATE rental_agreements 
SET license_plate = 'BI-78-FM' 
WHERE rental_agreement_number LIKE '06829%';

-- Update extracted_data JSON (plate field)
UPDATE rental_agreements 
SET extracted_data = jsonb_set(
    CAST(extracted_data AS jsonb),
    '{plate}',
    '"BI-78-FM"'
)
WHERE rental_agreement_number LIKE '06829%' 
AND extracted_data::text LIKE '%plate%';

-- Verify changes
SELECT 'AFTER UPDATE - Inspections:' as info;
SELECT inspection_number, vehicle_plate, contract_number, inspection_type 
FROM vehicle_inspections 
WHERE contract_number LIKE '06829%';

SELECT 'AFTER UPDATE - Rental Agreement:' as info;
SELECT rental_agreement_number, license_plate 
FROM rental_agreements 
WHERE rental_agreement_number LIKE '06829%';
