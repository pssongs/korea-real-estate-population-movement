CREATE TABLE IF NOT EXISTS seoul_population_flow (
    date INT,
    from_province VARCHAR(50),
    to_province VARCHAR(50),
    from_district VARCHAR(50),
    to_district VARCHAR(50),
    total_people INT,
    male INT,
    female INT,
    PRIMARY KEY (date, from_province, to_province, from_district, to_district)
)