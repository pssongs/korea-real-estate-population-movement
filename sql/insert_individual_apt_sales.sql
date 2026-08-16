INSERT INTO individual_apt_sales (
    apt_name,
    build_year,
    deal_date,
    floor,
    district_code
) VALUES (
    :apt_name,
    :build_year,
    :deal_date,
    :floor,
    :district_code
) ON CONFLICT DO NOTHING