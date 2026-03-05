-- Fix RA 6932: Create check-in inspection for AT-28-NX from AS-78-RH data
-- Execute this SQL in Railway PostgreSQL database

DO $$
DECLARE
    v_old_inspection_id INTEGER;
    v_new_inspection_id INTEGER;
    v_new_inspection_number TEXT;
    v_photo_count INTEGER;
    v_damage_count INTEGER;
    v_new_kms INTEGER;
    v_new_fuel TEXT;
    v_brand TEXT;
    v_model TEXT;
    v_customer_name TEXT;
    v_customer_email TEXT;
    v_customer_phone TEXT;
    v_inspector_name TEXT;
    v_inspector_notes TEXT;
    v_has_damage BOOLEAN;
    v_damage_count_val INTEGER;
    v_damage_severity TEXT;
    v_ai_complete BOOLEAN;
    v_ai_confidence DECIMAL;
    v_ai_damages INTEGER;
BEGIN
    -- Check if new inspection already exists
    IF EXISTS (
        SELECT 1 FROM vehicle_inspections
        WHERE contract_number LIKE '6932%'
          AND vehicle_plate = 'AT-28-NX'
          AND inspection_type = 'checkin'
    ) THEN
        RAISE NOTICE '⚠️ New inspection already exists for AT-28-NX, skipping';
        RETURN;
    END IF;

    -- Get swap data for new vehicle kms and fuel
    SELECT new_kms, new_fuel INTO v_new_kms, v_new_fuel
    FROM vehicle_swaps
    WHERE rental_agreement_number = '6932'
      AND old_plate = 'AS-78-RH'
      AND new_plate = 'AT-28-NX'
    ORDER BY swap_datetime DESC
    LIMIT 1;

    IF v_new_kms IS NULL THEN
        v_new_kms := 0;
        v_new_fuel := 'N/A';
        RAISE NOTICE '⚠️ No swap data found, using defaults';
    ELSE
        RAISE NOTICE '✅ Found swap: new_kms=%, new_fuel=%', v_new_kms, v_new_fuel;
    END IF;

    -- Get old inspection data
    SELECT id, vehicle_brand, vehicle_model, customer_name, customer_email, customer_phone,
           inspector_name, inspector_notes, has_damage, damage_count, damage_severity,
           ai_analysis_complete, ai_confidence_avg, ai_damages_detected
    INTO v_old_inspection_id, v_brand, v_model, v_customer_name, v_customer_email, v_customer_phone,
         v_inspector_name, v_inspector_notes, v_has_damage, v_damage_count_val, v_damage_severity,
         v_ai_complete, v_ai_confidence, v_ai_damages
    FROM vehicle_inspections
    WHERE contract_number LIKE '6932%'
      AND vehicle_plate = 'AS-78-RH'
      AND inspection_type = 'checkin'
    ORDER BY created_at DESC
    LIMIT 1;

    IF v_old_inspection_id IS NULL THEN
        RAISE EXCEPTION '❌ No old inspection found for AS-78-RH';
    END IF;

    RAISE NOTICE '✅ Found old inspection ID: %', v_old_inspection_id;

    -- Count photos
    SELECT COUNT(*) INTO v_photo_count
    FROM inspection_photos
    WHERE inspection_id = v_old_inspection_id;

    -- Generate new inspection number
    v_new_inspection_number := 'VI-' || TO_CHAR(NOW(), 'YYYYMMDD-HH24MISS');

    -- Create new inspection for AT-28-NX
    INSERT INTO vehicle_inspections 
    (inspection_number, inspection_type, vehicle_plate, vehicle_brand, vehicle_model,
     contract_number, customer_name, customer_email, customer_phone,
     inspector_name, inspector_notes, has_damage, damage_count, damage_severity,
     ai_analysis_complete, ai_confidence_avg, ai_damages_detected,
     odometer_reading, fuel_level, status, photo_count)
    VALUES (
        v_new_inspection_number,
        'checkin',
        'AT-28-NX',
        v_brand,
        v_model,
        '6932',
        v_customer_name,
        v_customer_email,
        v_customer_phone,
        v_inspector_name,
        v_inspector_notes,
        v_has_damage,
        v_damage_count_val,
        v_damage_severity,
        v_ai_complete,
        v_ai_confidence,
        v_ai_damages,
        v_new_kms,
        v_new_fuel,
        'completed',
        v_photo_count
    )
    RETURNING id INTO v_new_inspection_id;

    RAISE NOTICE '✅ Created new inspection ID: % (%)', v_new_inspection_id, v_new_inspection_number;

    -- Copy photos
    INSERT INTO inspection_photos
    (inspection_id, photo_type, photo_order, image_data, image_filename,
     image_size, image_format, ai_analyzed, ai_has_damage, ai_damage_type,
     ai_confidence, ai_result)
    SELECT v_new_inspection_id, photo_type, photo_order, image_data, image_filename,
           image_size, image_format, ai_analyzed, ai_has_damage, ai_damage_type,
           ai_confidence, ai_result
    FROM inspection_photos
    WHERE inspection_id = v_old_inspection_id;

    GET DIAGNOSTICS v_photo_count = ROW_COUNT;
    RAISE NOTICE '✅ Copied % photo(s)', v_photo_count;

    -- Copy damages if they exist
    SELECT COUNT(*) INTO v_damage_count
    FROM inspection_damages
    WHERE inspection_id = v_old_inspection_id;

    IF v_damage_count > 0 THEN
        INSERT INTO inspection_damages
        (inspection_id, damage_type, damage_position_x, damage_position_y,
         damage_description, damage_severity, photo_reference)
        SELECT v_new_inspection_id, damage_type, damage_position_x, damage_position_y,
               damage_description, damage_severity, photo_reference
        FROM inspection_damages
        WHERE inspection_id = v_old_inspection_id;

        GET DIAGNOSTICS v_damage_count = ROW_COUNT;
        RAISE NOTICE '✅ Copied % damage(s)', v_damage_count;
    END IF;

    RAISE NOTICE '✅ RA 6932 fixed successfully! You can now checkout AT-28-NX';
END $$;
