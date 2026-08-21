SELECT 
    from_district,
    date / 100 AS year,
    SUM(total_people) AS total_outflow
FROM seoul_population_flow
WHERE date < 202601
  AND from_district <> to_district
  AND from_district IN ('강남구', '송파구', '강동구', '서초구', '관악구')
GROUP BY from_district, date / 100
ORDER BY year, total_outflow DESC;