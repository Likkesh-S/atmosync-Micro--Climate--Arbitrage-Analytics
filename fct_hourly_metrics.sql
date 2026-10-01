/*
AtmoSync - Hourly Telemetry Fact Model

Purpose:
- Aggregate cleaned telemetry by container and hour
- Produce analytics-ready environmental metrics
- Serve as the main Snowflake/dbt fact table for dashboards

Output:
ATMOSYNC.DEV.FCT_HOURLY_METRICS
*/

{{ config(
    materialized='table',
    alias='FCT_HOURLY_METRICS'
) }}

with telemetry as (

    select
        container_id,
        telemetry_hour,
        temperature_c,
        humidity_pct,
        ping_status
    from {{ ref('stg_telemetry') }}

),

hourly_metrics as (

    select
        container_id,
        telemetry_hour,

        count(*) as telemetry_count,

        count_if(
            upper(ping_status) in ('SUCCESS', 'OK', 'ONLINE')
        ) as successful_ping_count,

        avg(temperature_c) as avg_temp_c,
        max(temperature_c) as peak_temp_c,
        min(temperature_c) as min_temp_c,

        avg(humidity_pct) as avg_humidity_pct,

        max(temperature_c) - min(temperature_c)
            as temperature_range_c

    from telemetry

    group by
        container_id,
        telemetry_hour

)

select
    container_id,
    telemetry_hour,
    telemetry_count,
    successful_ping_count,
    round(avg_temp_c, 2) as avg_temp_c,
    round(peak_temp_c, 2) as peak_temp_c,
    round(min_temp_c, 2) as min_temp_c,
    round(avg_humidity_pct, 2) as avg_humidity_pct,
    round(temperature_range_c, 2) as temperature_range_c

from hourly_metrics
