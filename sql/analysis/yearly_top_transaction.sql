SELECT
  d.district,
  deal_date/100 as deal_year,
  COUNT(*) as transaction_count
FROM individual_apt_sales i 
  LEFT JOIN district_code_dim d
  ON i.district_code = LEFT(d.code,5)
WHERE i.deal_date <= 202512 
  AND i.deal_date >= 202301
  AND d.district IN (
      '송파구',
      '노원구',
      '강동구',
      '강남구',
      '성북구'
  )
GROUP BY d.district, deal_date/100
ORDER BY deal_year, transaction_count DESC;
