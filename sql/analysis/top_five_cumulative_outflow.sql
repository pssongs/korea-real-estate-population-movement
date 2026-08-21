SELECT 
    from_district,
    SUM(total_people) as total_outflow
FROM seoul_population_flow
WHERE date < 202601
  AND from_district <> to_district
GROUP BY from_district
ORDER BY total_outflow DESC
LIMIT 5;