CREATE TABLE IF NOT EXISTS seoul_apartment_sales (
    month INT,
    district VARCHAR(50),
    units_sold INT,
    PRIMARY KEY (month, district)
)