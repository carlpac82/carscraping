# Mapeamento de Campos - Livro de Reservas

## Query SQL e Índices

```sql
SELECT 
    cb.id,                    -- 0
    cb.commissioner_id,       -- 1
    cb.voucher_number,        -- 2  ✓
    cb.client_name,           -- 3  ✓
    cb.client_email,          -- 4  ✓
    cb.client_phone,          -- 5  ✓
    cb.hotel,                 -- 6  ✓
    cb.room_number,           -- 7  ✓
    cb.pickup_date,           -- 8  ✓ (dividido em day/month/year)
    cb.pickup_time,           -- 9  ✓ (dividido em hour/minute)
    cb.dropoff_date,          -- 10 ✓ (dividido em day/month/year)
    cb.dropoff_time,          -- 11 ✓ (dividido em hour/minute)
    cb.pickup_location,       -- 12 ✓
    cb.dropoff_location,      -- 13 ✓
    cb.vehicle_group,         -- 14 ✓
    cb.extras,                -- 15 ✓ (processado e formatado)
    cb.flight_number,         -- 16 ✓
    cb.language,              -- 17
    cb.observations,          -- 18 ✓
    cb.deposit,               -- 19 ✓
    cb.price,                 -- 20 ✓
    cb.status,                -- 21
    cb.created_at,            -- 22 ✓ (dividido em day/month/year)
    cb.updated_at,            -- 23
    c.name as commissioner_name -- 24 ✓
```

## Campos Mapeados no PDF

### Dados do Cliente
- `voucher_number` → row[2]
- `client_name` → row[3]
- `client_email` → row[4]
- `client_phone` → row[5]
- `hotel_name` → row[6]
- `room_number` → row[7]
- `flight_number` → row[16]

### Data de Levantamento
- `pickup_day` → extraído de row[8]
- `pickup_month` → extraído de row[8]
- `pickup_year` → extraído de row[8]
- `pickup_hour` → extraído de row[9]
- `pickup_minute` → extraído de row[9]
- `pickup_location` → row[12]

### Data de Devolução
- `dropoff_day` → extraído de row[10]
- `dropoff_month` → extraído de row[10]
- `dropoff_year` → extraído de row[10]
- `dropoff_hour` → extraído de row[11]
- `dropoff_minute` → extraído de row[11]
- `dropoff_location` → row[13]

### Veículo e Duração
- `vehicle_group` → row[14]
- `rental_days` → calculado (dropoff_date - pickup_date)

### Datas da Reserva
- `booking_day` → extraído de row[22] (created_at)
- `booking_month` → extraído de row[22] (created_at)
- `booking_year` → extraído de row[22] (created_at)

### Depósito
- `deposit_amount` → row[19]
- `deposit_day` → vazio (futuro)
- `deposit_month` → vazio (futuro)
- `deposit_year` → vazio (futuro)

### Preços
- `base_price` → calculado com base nas configurações
- `premium_insurance` → calculado com base nas configurações
- `road_tax` → calculado com base nas configurações
- `extras_total` → calculado da soma dos extras
- `price` → row[20]

### Extras Detalhados
- `driver_extras` → formatado de row[15] (AD/YD/SD)
- `seat_extras` → formatado de row[15] (BA/BO)
- `location_extras` → formatado de row[15] (A/SP)
- `other_extras` → formatado de row[15] (GPS, etc)

### Comissionista e Observações
- `commissioner_name` → row[24]
- `observations` → row[18]

## Campos Disponíveis para Mapear no Frontend

Todos os campos acima estão disponíveis em `FIELDS_TO_MAP` no arquivo:
`/Users/filipepacheco/CascadeProjects/carscraping/templates/commissioner_booking_mapper.html`
