/*
AtmoSync - Data Quality Test
File: fct_hourly_metrics_tests.sql

Purpose:
Verify that hourly metrics contain valid environmental values.

The test returns rows that violate the expected conditions.
If the query returns zero rows, the test passes.
*/

with metrics as (

    select
        container_id,
        telemetry_hour,
        telemetry_count,
        successful_ping_count,
        avg_temp_c,
        peak_temp_c,
        min_temp_c,
        avg_humidity_pct,
        temperature_range_c

    from {{ ref('fct_hourly_metrics') }}

)

select *

from metrics

where
    container_id is null

    or telemetry_hour is null

    or telemetry_count <= 0

    or successful_ping_count < 0

    or successful_ping_count > telemetry_count

    or avg_humidity_pct < 0

    or avg_humidity_pct > 100

    or peak_temp_c < min_temp_c

    or temperature_range_c < 
0
