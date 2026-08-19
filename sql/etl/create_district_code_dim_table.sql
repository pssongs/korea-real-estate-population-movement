CREATE TABLE IF NOT EXISTS district_code_dim (
    code varchar(10),
    district varchar(50),
    PRIMARY KEY(code, district)
) 