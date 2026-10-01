# AtmoSync System Architecture

## 1. Overview

AtmoSync: Micro-Climate Arbitrage Analytics is an end-to-end IoT and data analytics platform that converts environmental telemetry into structured analytical insights.

The architecture combines streaming, cloud data warehousing, data transformation, analytics, and business intelligence.

## 2. High-Level Architecture

```text
┌──────────────────────────────┐
│ IoT / Micro-Climate Simulator│
│ Temperature                  │
│ Humidity                     │
│ Device Telemetry             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Apache Kafka                 │
│ Real-Time Data Streaming     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Snowflake RAW                │
│ Raw Telemetry Storage        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ dbt                          │
│ Cleaning & Transformation    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ STG_TELEMETRY                │
│ Cleaned Telemetry            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ FCT_HOURLY_METRICS           │
│ Hourly Analytical Metrics    │
└──────────────┬───────────────┘
               │
               ├─────────────────────┐
               ▼                     ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│ Micro-Climate Analytics      │  │ Anomaly Detection            │
│ Temperature / Humidity       │  │ Unusual Conditions           │
│ Trends & Comparisons         │  │                               │
└──────────────┬───────────────┘  └──────────────┬───────────────┘
               │                                  │
               └────────────────┬─────────────────┘
                                ▼
                 ┌──────────────────────────────┐
                 │ Arbitrage Analytics          │
                 │ Environmental Differences    │
                 │ Opportunity Analysis         │
                 └──────────────┬───────────────┘
                                │
                                ▼
                 ┌──────────────────────────────┐
                 │ BI Dashboard                 │
                 │ Apache Superset / Power BI   │
                 └──────────────────────────────┘
```

## 3. Architecture Components

### 3.1 IoT / Micro-Climate Simulator

The simulator generates environmental telemetry representing multiple monitored environments.

Typical attributes include:

- `container_id`
- `timestamp`
- `temperature_c`
- `humidity_pct`
- `ping_status`

The simulator allows the project to reproduce realistic streaming conditions without requiring physical IoT sensors.

### 3.2 Apache Kafka

Kafka acts as the streaming layer.

Its responsibilities include:

- Receiving telemetry events
- Organizing events into topics
- Supporting continuous data ingestion
- Decoupling the data producer from downstream systems

Example topic:

```text
atmosync.telemetry
```

### 3.3 Snowflake RAW Layer

Raw telemetry is stored in Snowflake before transformation.

A typical raw table may contain:

```text
ATMOSYNC
└── DEV
    └── RAW_TELEMETRY
```

The RAW layer preserves incoming data and provides the source for downstream transformation.

### 3.4 dbt Transformation Layer

dbt is responsible for transforming raw telemetry into analytics-ready datasets.

The transformation process includes:

- Data type standardization
- Timestamp processing
- Null handling
- Data validation
- Metric calculation
- Hourly aggregation

### 3.5 STG_TELEMETRY

The staging model provides a cleaned representation of the raw telemetry.

Example:

```text
STG_TELEMETRY
```

Possible standardized columns:

```text
CONTAINER_ID
TELEMETRY_TIMESTAMP
TEMPERATURE_C
HUMIDITY_PCT
PING_STATUS
```

### 3.6 FCT_HOURLY_METRICS

The fact model aggregates telemetry by container and hour.

Example columns:

```text
TELEMETRY_HOUR
CONTAINER_ID
PING_COUNT
AVG_TEMP_C
PEAK_TEMP_C
MIN_TEMP_C
AVG_HUMIDITY_PCT
```

This table acts as the primary analytical dataset for the project.

## 4. Analytics Layer

The analytics layer uses the hourly fact table to calculate environmental indicators.

### Temperature Analytics

Examples include:

- Average temperature
- Temperature range
- Temperature change
- Cross-location temperature difference

### Humidity Analytics

Examples include:

- Average humidity
- Humidity range
- Humidity change
- Cross-location humidity difference

### Temporal Analytics

The system can analyze:

- Hourly patterns
- Daily patterns
- Peak environmental periods
- Stable environmental periods

## 5. Anomaly Detection

Anomaly detection identifies observations that differ significantly from expected environmental behavior.

Potential techniques include:

- Statistical thresholds
- Z-score analysis
- Interquartile range
- Isolation Forest
- Rolling averages

An anomaly does not automatically indicate a system failure. It represents an observation that requires further investigation.

## 6. Arbitrage Analytics

The arbitrage layer compares environmental conditions across monitored locations or time periods.

Example:

```text
Container A
Average Temperature = 24.0°C
Average Humidity    = 55%

Container B
Average Temperature = 29.0°C
Average Humidity    = 72%
```

Derived differences:

```text
Temperature Difference = 5.0°C
Humidity Difference    = 17 percentage points
```

These differences can be evaluated against predefined operational rules to identify potential opportunities.

The analysis is intended to support data-driven investigation rather than assume that every environmental difference produces a financial opportunity.

## 7. Visualization Layer

The final analytical data can be connected to:

- Apache Superset
- Power BI
- Streamlit
- Other BI tools

Suggested dashboard sections:

### Overview

- Total telemetry events
- Number of monitored environments
- Average temperature
- Average humidity

### Temperature Analysis

- Temperature trend
- Minimum / maximum temperature
- Environment comparison

### Humidity Analysis

- Humidity trend
- Environment comparison
- High-humidity periods

### Anomaly Analysis

- Anomaly count
- Anomaly timeline
- Affected environments

### Arbitrage Analysis

- Environmental differences
- Opportunity indicators
- Location/time comparisons

## 8. Data Flow

The complete data flow is:

```text
Generate
   ↓
Stream
   ↓
Store
   ↓
Clean
   ↓
Transform
   ↓
Aggregate
   ↓
Analyze
   ↓
Detect Anomalies
   ↓
Compare Conditions
   ↓
Identify Potential Opportunities
   ↓
Visualize
```

## 9. Data Engineering Principles

AtmoSync follows these principles:

- Separate raw and transformed data
- Keep transformations reproducible
- Use modular dbt models
- Validate analytical data
- Keep credentials outside source control
- Document assumptions
- Make analytical outputs traceable to source telemetry

## 10. Scalability

The architecture can be expanded by:

- Increasing Kafka partitions
- Adding more sensor sources
- Increasing Snowflake compute capacity
- Creating additional dbt models
- Introducing real-time processing
- Adding machine-learning models
- Connecting additional BI tools

## 11. Security Considerations

Sensitive credentials should never be committed to GitHub.

Credentials should be stored using:

```text
.env
Environment Variables
Secret Managers
Cloud Secret Stores
```

The repository `.gitignore` excludes common credential and environment files.

## 12. Final Architecture Goal

AtmoSync is designed to demonstrate a complete modern data platform:

```text
IoT
 ↓
Streaming
 ↓
Cloud Data Warehouse
 ↓
Transformation
 ↓
Data Modeling
 ↓
Analytics
 ↓
Anomaly Detection
 ↓
Micro-Climate Opportunity Analysis
 ↓
Business Intelligence
```
