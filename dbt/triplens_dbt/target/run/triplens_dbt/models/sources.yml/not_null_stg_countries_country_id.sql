select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select country_id
from TRIPLENS.STAGING.stg_countries
where country_id is null



      
    ) dbt_internal_test