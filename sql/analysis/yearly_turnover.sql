SELECT
    district,
    year,
    SUM(outflow)::INT AS total_outflow,
    SUM(inflow)::INT AS total_inflow,
    SUM(outflow)::INT + SUM(inflow)::INT AS turnover
FROM (
    -- Outflow
    SELECT
        from_district AS district,
        (date / 100)::INT AS year,
        SUM(total_people) AS outflow,
        0 AS inflow
    FROM seoul_population_flow
    WHERE date < 202601
      AND from_district <> to_district
      AND from_district IN (
      '강남구',
      '송파구',
      '강동구',
      '서초구',
      '관악구',
      '동작구',
      '영등포구'
  )
    GROUP BY from_district, (date / 100)::INT

    UNION ALL

    -- Inflow
    SELECT
        to_district AS district,
        (date / 100)::INT AS year,
        0 AS outflow,
        SUM(total_people) AS inflow
    FROM seoul_population_flow
    WHERE date < 202601
      AND from_district <> to_district
      AND to_district IN (
      '강남구',
      '송파구',
      '강동구',
      '서초구',
      '관악구',
      '동작구',
      '영등포구'
  )
    GROUP BY to_district, (date / 100)::INT
) movement
GROUP BY district, year
ORDER BY year, turnover DESC;