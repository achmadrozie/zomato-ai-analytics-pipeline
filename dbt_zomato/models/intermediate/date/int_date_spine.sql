WITH generated_dates AS (
    SELECT
        DATEADD(DAY, SEQ4(), '2024-01-01'::DATE) AS date_day
    FROM TABLE(GENERATOR(ROWCOUNT => 1200))
)

SELECT date_day
FROM generated_dates
WHERE date_day <= '2026-12-31'::DATE
