WITH inflow AS (
  SELECT
    to_district,
    date,
    SUM(total_people) AS inflow
  FROM seoul_population_flow
  WHERE to_district <> from_district
    AND date::INT <= 202512
    AND date::INT >= 202301
    AND to_district IN ('강남구','송파구','강동구')
  GROUP BY to_district, date
),
outflow AS (
    SELECT
    from_district,
    date,
    SUM(total_people) AS outflow
  FROM seoul_population_flow
  WHERE to_district <> from_district
    AND date::INT <= 202512
    AND date::INT >= 202301
    AND from_district IN ('강남구','송파구','강동구')
  GROUP BY from_district, date
)
SELECT 
  i.to_district AS district,
  i.date::INT,
  i.inflow,
  o.outflow,
  COALESCE(i.inflow,0) + COALESCE(o.outflow,0) AS turnover
FROM inflow i 
LEFT JOIN outflow o 
  ON i.to_district = o.from_district
  AND i.date = o.date
ORDER BY date