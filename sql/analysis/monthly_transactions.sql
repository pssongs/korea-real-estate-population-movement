SELECT
  d.district,
  i.deal_date::INT AS date,
  COUNT(*) AS transactions
FROM individual_apt_sales i
LEFT JOIN district_code_dim d
  ON i.district_code = LEFT(d.code,5)
WHERE i.deal_date::INT <= 202512
  AND i.deal_date::INT >= 202301
  AND d.district IN ('강남구','강동구','송파구')
GROUP BY district, deal_date
ORDER BY date, transactions DESC