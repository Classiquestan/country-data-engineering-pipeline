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

FROM TRIPLENS.STAGING.stg_countries




-- SELECT
--     country_id,
--     country_name,
--     official_name,

--     iso_alpha_2,
--     iso_alpha_3,

--     region,
--     subregion,
--     continent,

--     population,
--     area_km2,

--     latitude,
--     longitude,

--     government_type,
--     capital_name,

--     currency_code,
--     currency_name,

--     is_landlocked,

--     SOURCE_FILE,
--     INGESTION_TIMESTAMP

-- FROM TRIPLENS.STAGING.stg_countries





-- SELECT
--     RAW_DATA:uuid::STRING AS country_id,
--     RAW_DATA:names.common::STRING AS country_name,
--     RAW_DATA:names.official::STRING AS official_name,

--     RAW_DATA:codes.alpha_2::STRING AS iso_alpha_2,
--     RAW_DATA:codes.alpha_3::STRING AS iso_alpha_3,

--     RAW_DATA:region::STRING AS region,
--     RAW_DATA:subregion::STRING AS subregion,

--     RAW_DATA:population::NUMBER AS population,
--     RAW_DATA:area.kilometers::FLOAT AS area_km2,

--     RAW_DATA:coordinates.lat::FLOAT AS latitude,
--     RAW_DATA:coordinates.lng::FLOAT AS longitude,

--     RAW_DATA:government_type::STRING AS government_type,

--     RAW_DATA:capitals[0].name::STRING AS capital_name,
--     RAW_DATA:continent::STRING AS continent,

--     RAW_DATA:currencies[0].code::STRING AS currency_code,
--     RAW_DATA:currencies[0].name::STRING AS currency_name,

--     RAW_DATA:languages[0].name::STRING AS language_name,

--     RAW_DATA:timezones[0]::STRING AS timezone,

--     SOURCE_FILE,
--     INGESTION_TIMESTAMP

-- FROM TRIPLENS.STAGING.COUNTRIES_RAW