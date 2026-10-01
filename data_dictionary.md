# AtmoSync Data Dictionary

## 1. Overview

This document defines the main fields used in the AtmoSync IoT telemetry
and analytics pipeline.

Pipeline:

IoT Simulator → Kafka → Snowflake RAW → dbt Staging → Hourly Metrics → Analytics

---

## 2. Raw Telemetry Dataset

Source table:

`ATMOSYNC.RAW.TELEMETRY`

| Column | Data Type | Description |
|---|---|---|
| CONTAINER_ID | VARCHAR | Unique identifier of the monitored container. |
| TELEMETRY_HOUR | TIMESTAMP | Timestamp associated with the telemetry observation. |
| TEMPERATURE_C | FLOAT | Temperature measurement in degrees Celsius. |
| HUMIDITY_PCT | FLOAT | Relative humidity measurement as a percentage. |
| PING_STATUS | VARCHAR | Connectivity or telemetry status. |
| INGESTED_AT | TIMESTAMP | Timestamp when the record was ingested into Snowflake. |

---

## 3. Staging Model

Model:

`ATMOSYNC.DEV.STG_TELEMETRY`

The staging model standardizes data types, cleans status values, and removes
duplicate telemetry records.

| Column | Data Type | Description |
|---|---|---|
| container_id | VARCHAR | Standardized container identifier. |
| telemetry_hour | TIMESTAMP | Standardized telemetry timestamp. |
| temperature_c | FLOAT | Cleaned temperature in degrees Celsius. |
| humidity_pct | FLOAT | Cleaned relative humidity percentage. |
| ping_status | VARCHAR | Standardized telemetry status. |
| ingested_at | TIMESTAMP | Snowflake ingestion timestamp. |

---

## 4. Hourly Fact Model

Model:

`ATMOSYNC.DEV.FCT_HOURLY_METRICS`

| Column | Data Type | Description |
|---|---|---|
| container_id | VARCHAR | Container identifier. |
| telemetry_hour | TIMESTAMP | Hour used for aggregation. |
| telemetry_count | INTEGER | Number of telemetry records during the hour. |
| successful_ping_count | INTEGER | Number of successful connectivity pings. |
| avg_temp_c | FLOAT | Average temperature during the hour. |
| peak_temp_c | FLOAT | Maximum temperature during the hour. |
| min_temp_c | FLOAT | Minimum temperature during the hour. |
| avg_humidity_pct | FLOAT | Average relative humidity during the hour. |
| temperature_range_c | FLOAT | Difference between peak and minimum temperature. |

---

## 5. Feature Engineering Fields

| Feature | Description |
|---|---|
| hour | Hour of the day from 0 to 23. |
| day_of_week | Numeric day of the week. |
| day_name | Name of the day. |
| is_weekend | Indicates whether the observation occurs on a weekend. |
| hour_sin | Cyclical sine encoding of the hour. |
| hour_cos | Cyclical cosine encoding of the hour. |
| temperature_change_c | Temperature change from the previous observation. |
| temperature_rolling_mean_3h | Three-observation rolling temperature mean. |
| temperature_rolling_std_3h | Three-observation rolling temperature standard deviation. |
| temperature_deviation_c | Difference between current temperature and rolling mean. |
| humidity_change_pct_points | Humidity change from the previous observation. |
| humidity_rolling_mean_3h | Three-observation rolling humidity mean. |
| humidity_rolling_std_3h | Three-observation rolling humidity standard deviation. |
| humidity_deviation_pct_points | Difference between current humidity and rolling mean. |
| temperature_humidity_interaction | Temperature multiplied by humidity. |

---

## 6. Anomaly Detection Fields

| Field | Description |
|---|---|
| temperature_range_anomaly | Flags temperature values outside configured limits. |
| humidity_range_anomaly | Flags humidity values outside configured limits. |
| temperature_change_anomaly | Flags unusually large temperature changes. |
| humidity_change_anomaly | Flags unusually large humidity changes. |
| rule_anomaly_score | Number of rule-based anomaly conditions triggered. |
| rule_based_anomaly | Combined rule-based anomaly flag. |
| isolation_forest_anomaly | Anomaly flag produced by Isolation Forest. |
| isolation_forest_score | Isolation Forest decision score. |
| combined_anomaly | Combined anomaly indicator. |

---

## 7. Micro-Climate Arbitrage Analytics

| Field | Description |
|---|---|
| temperature_deviation_c | Absolute difference from target temperature. |
| humidity_deviation_pct_points | Absolute difference from target humidity. |
| temperature_range_c | Difference between hourly peak and minimum temperature. |
| temperature_rank | Relative temperature-condition rank within an hour. |
| humidity_rank | Relative humidity-condition rank within an hour. |
| environmental_score | Relative score based on distance from target conditions. |
| hourly_temperature_spread_c | Difference between highest and lowest container temperature. |
| hourly_humidity_spread_pct | Difference between highest and lowest container humidity. |
| temperature_spread_opportunity | Flags a temperature spread above the configured threshold. |
| humidity_spread_opportunity | Flags a humidity spread above the configured threshold. |
| arbitrage_opportunity | Combined relative micro-climate opportunity indicator. |
| opportunity_strength | Relative strength calculated from environmental spreads. |

---

## 8. Data Quality Rules

1. `CONTAINER_ID` should not be NULL.
2. `TELEMETRY_HOUR` should not be NULL.
3. Temperature is measured in degrees Celsius.
4. Humidity should normally remain between 0 and 100%.
5. Hourly telemetry counts should be greater than zero.
6. Successful ping counts should not exceed total telemetry counts.
7. Peak temperature should be greater than or equal to minimum temperature.
8. Temperature range should not be negative.
9. Duplicate telemetry records should be removed during staging.

---

## 9. Units

| Measurement | Unit |
|---|---|
| Temperature | °C |
| Humidity | % |
| Temperature change | °C |
| Humidity change | Percentage points |
| Time | Timestamp / hourly |
| Counts | Number of records or events |

---

## 10. Micro-Climate Arbitrage Note

In AtmoSync, **micro-climate arbitrage** means identifying relative
differences in environmental conditions between monitored containers
or locations.

The opportunity indicators are analytics outputs for comparison and
decision support. They do not execute financial trades or transactions.
