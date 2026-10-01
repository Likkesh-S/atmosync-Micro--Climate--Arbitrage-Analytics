/*
===========================================================
AtmoSync - Raw Telemetry Table
File: create_raw_telemetry.sql

Purpose:
Create the RAW telemetry table used to store IoT sensor
data before dbt transformation.

Pipeline:
IoT Simulator → Kafka → Snowflake RAW → dbt → Analytics
===========================================================
*/

-- Create the RAW schema if it does not already exist
CREATE SCHEMA IF NOT EXISTS ATMOSYNC.RAW;

-- Create the raw telemetry table
CREATE TABLE IF NOT EXISTS ATMOSYNC.RAW.TELEMETRY
(
    CONTAINER_ID       VARCHAR(100) NOT NULL,
    TELEMETRY_HOUR     TIMESTAMP_NTZ NOT NULL,
    TEMPERATURE_C      FLOAT,
    HUMIDITY_PCT       FLOAT,
    PING_STATUS        VARCHAR(50),
    INGESTED_AT        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Add table-level documentation
COMMENT ON TABLE ATMOSYNC.RAW.TELEMETRY IS
'Raw IoT telemetry data received from the AtmoSync ingestion pipeline.';

-- Add column documentation
COMMENT ON COLUMN ATMOSYNC.RAW.TELEMETRY.CONTAINER_ID IS
'Unique identifier of the monitored container.';

COMMENT ON COLUMN ATMOSYNC.RAW.TELEMETRY.TELEMETRY_HOUR IS
'Timestamp associated with the telemetry observation.';

COMMENT ON COLUMN ATMOSYNC.RAW.TELEMETRY.TEMPERATURE_C IS
'Temperature measurement in degrees Celsius.';

COMMENT ON COLUMN ATMOSYNC.RAW.TELEMETRY.HUMIDITY_PCT IS
'Relative humidity measurement as a percentage.';

COMMENT ON COLUMN ATMOSYNC.RAW.TELEMETRY.PING_STATUS IS
'Connectivity or telemetry status of the container.';

COMMENT ON COLUMN ATMOSYNC.RAW.TELEMETRY.INGESTED_AT IS
'Timestamp when the telemetry record was ingested into Snowflake.';


-- Verify the table structure
DESCRIBE TABLE ATMOSYNC.RAW.TELEMETRY;


-- Verify that the table can be queried
SELECT *
FROM ATMOSYNC.RAW.TELEMETRY
LIMIT 10;
