SELECT
    country_id,

    TRIM(country_name) AS country_name,
    TRIM(official_name) AS official_name,

    UPPER(iso_alpha_2) AS iso_alpha_2,
    UPPER(iso_alpha_3) AS iso_alpha_3,

    region,
    subregion,
    continent,

    population,
    area_km2,

    -- Derived metric
    ROUND(
        population / NULLIF(area_km2, 0),
        2
    ) AS population_density,

    -- Geographic information
    latitude,
    longitude,

    government_type,
    capital_name,

    currency_code,
    currency_name,

    is_landlocked,

    -- Derived classification
    CASE
        WHEN population >= 100000000 THEN 'Very Large'
        WHEN population >= 50000000 THEN 'Large'
        WHEN population >= 10000000 THEN 'Medium'
        ELSE 'Small'
    END AS population_category,

    SOURCE_FILE,
    INGESTION_TIMESTAMP

FROM {{ ref('stg_countries') }}


