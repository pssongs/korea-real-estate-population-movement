SELECT
    d.district,
    COUNT(*) AS transaction_count
FROM individual_apt_sales i
LEFT JOIN district_code_dim d
    ON i.district_code = LEFT(d.code, 5)
WHERE DATE_PART('year',TO_DATE(deal_date::TEXT,'YYYYMM')) >= 2023
  AND DATE_PART('year',TO_DATE(deal_date::TEXT,'YYYYMM')) <= 2025
GROUP BY d.district
ORDER BY transaction_count DESC
LIMIT 5;
