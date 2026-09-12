select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

select
    iso_alpha_3 as unique_field,
    count(*) as n_records

from TRIPLENS.STAGING.stg_countries
where iso_alpha_3 is not null
group by iso_alpha_3
having count(*) > 1



      
    ) dbt_internal_test