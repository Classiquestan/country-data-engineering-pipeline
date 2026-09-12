
  
    

        create or replace transient table TRIPLENS.STAGING.stg_countries
         as
        (WITH source_data AS (

    SELECT
        RAW_DATA,
        SOURCE_FILE,
        INGESTION_TIMESTAMP
    FROM TRIPLENS.STAGING.COUNTRIES_RAW

),

countries AS (

    SELECT
        value AS country,
        SOURCE_FILE,
        INGESTION_TIMESTAMP
    FROM source_data,
    LATERAL FLATTEN(
        input => RAW_DATA:data:objects
    )

)

SELECT

    -- Identity
    country:uuid::STRING AS country_id,

    -- Names
    country:names:common::STRING AS country_name,
    country:names:official::STRING AS official_name,

    -- ISO codes
    country:codes:alpha_2::STRING AS iso_alpha_2,
    country:codes:alpha_3::STRING AS iso_alpha_3,

    -- Geography
    country:region::STRING AS region,
    country:subregion::STRING AS subregion,
    country:continents[0]::STRING AS continent,

    country:coordinates:lat::FLOAT AS latitude,
    country:coordinates:lng::FLOAT AS longitude,

    country:area:kilometers::FLOAT AS area_km2,

    -- Demographics
    country:population::NUMBER AS population,

    -- Government
    country:government_type::STRING AS government_type,

    -- Capital
    country:capitals[0]:name::STRING AS capital_name,

    -- Currency
    country:currencies[0]:code::STRING AS currency_code,
    country:currencies[0]:name::STRING AS currency_name,

    -- Other useful information
    country:landlocked::BOOLEAN AS is_landlocked,

    -- Metadata
    SOURCE_FILE,
    INGESTION_TIMESTAMP

FROM countries
        );
      
  