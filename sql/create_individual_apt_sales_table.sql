CREATE TABLE IF NOT EXISTS individual_apt_sales (
    id SERIAL PRIMARY KEY,
    apt_name varchar(50),
    build_year varchar(4),
    deal_date varchar(6),
    floor varchar(3),
    district_code varchar(5)
)