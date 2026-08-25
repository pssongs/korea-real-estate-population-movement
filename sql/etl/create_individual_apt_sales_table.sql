CREATE TABLE IF NOT EXISTS individual_apt_sales (
    id SERIAL PRIMARY KEY,
    apt_name varchar(50),
    build_year INTEGER,
    deal_date INTEGER,
    floor INTEGER,
    district_code varchar(5),
    price_manwon INTEGER,
    size_m2 NUMERIC,
    unit varchar(20),
    dong varchar(10)
)