
    
    

select
    iso_alpha_3 as unique_field,
    count(*) as n_records

from TRIPLENS.STAGING.stg_countries
where iso_alpha_3 is not null
group by iso_alpha_3
having count(*) > 1


