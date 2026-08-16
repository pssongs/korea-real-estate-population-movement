INSERT INTO seoul_population_flow (
    date,
    from_province,
    to_province,
    from_district,
    to_district,
    total_people,
    male,
    female
) VALUES (
    :date,
    :from_province,
    :to_province,
    :from_district,
    :to_district,
    :total_people,
    :male,
    :female
)
ON CONFLICT (date, from_province, to_province, from_district, to_district) DO NOTHING
