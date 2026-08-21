SELECT 
    to_district,
    date / 100 AS year,
    SUM(total_people) AS total_inflow
FROM seoul_population_flow
WHERE date < 202601
  AND from_district <> to_district
  AND to_district IN ('송파구', '강남구', '관악구', '동작구', '영등포구')
GROUP BY to_district, date / 100
ORDER BY year, total_inflow DESC;


