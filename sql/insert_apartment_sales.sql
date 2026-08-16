INSERT INTO seoul_apartment_sales (
    month,
    district,
    units_sold
) VALUES (
    :month,
    :district,
    :units_sold
)
ON CONFLICT (month, district) DO NOTHING