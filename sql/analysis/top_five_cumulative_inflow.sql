SELECT 
    to_district,
    SUM(total_people) as total_inflow
FROM seoul_population_flow
WHERE date < 202601
  AND from_district <> to_district
GROUP BY to_district
ORDER BY total_inflow DESC
LIMIT 5;