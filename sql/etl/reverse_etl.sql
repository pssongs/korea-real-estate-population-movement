SELECT
  d.district,
  i.deal_date::INT AS month,
  ROUND(
    SUM(price_manwon)/SUM(size_m2)
    ,2) AS weighted_avg_price_m2
FROM individual_apt_sales i
LEFT JOIN district_code_dim d
  ON i.district_code = LEFT(d.code,5)
WHERE i.deal_date::INT BETWEEN 202301 AND 202512
GROUP BY district, deal_date
ORDER BY month;