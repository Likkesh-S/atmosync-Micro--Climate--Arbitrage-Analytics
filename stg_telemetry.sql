/*
AtmoSync - Staging Telemetry Model

Purpose:
- Read telemetry from the Snowflake RAW layer
- Standardize column names and data types
- Remove duplicate records
- Create clean fields for downstream analytics

Expected source:
ATMOSYNC.RAW.TELEMETRY
*/

{{ config(
    materialized='view',
    alias='STG_TELEMETRY'
) }}

with source_data as (

    select
        container_id,
        telemetry_hour,
        temperature_c,
        humidity_pct,
        ping_status,
        ingested_at
    from {{ source('raw', 'TELEMETRY') }}

),

cleaned as (

    select
        cast(container_id as varchar) as container_id,

        cast(telemetry_hour as timestamp) as telemetry_hour,

        cast(temperature_c as float) as temperature_c,

        cast(humidity_pct as float) as humidity_pct,

        upper(trim(cast(ping_status as varchar))) as ping_status,

        cast(ingested_at as timestamp) as ingested_at

    from source_data

),

deduplicated as (

    select
        *,
        row_number() over (
            partition by
                container_id,
                telemetry_hour,
                temperature_c,
                humidity_pct,
                ping_status
            order by ingested_at desc
        ) as row_num

    from cleaned

)

select
    container_id,
    telemetry_hour,
    temperature_c,
    humidity_pct,
    ping_status,
    ingested_at

from deduplicated

where row_num = 1
