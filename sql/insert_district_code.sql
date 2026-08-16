INSERT INTO district_code_dim (
    code,
    district
) VALUES (
    :code,
    :district
) ON CONFLICT DO NOTHING