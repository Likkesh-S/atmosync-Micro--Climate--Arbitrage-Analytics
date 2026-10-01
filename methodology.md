# AtmoSync Analytics Methodology

## 1. Purpose

This document describes the methodology used by AtmoSync: Micro-Climate Arbitrage Analytics to transform raw environmental telemetry into reliable analytical insights.

The methodology covers data ingestion, cleaning, transformation, aggregation, exploratory analysis, anomaly detection, micro-climate comparison, and opportunity analysis.

---

## 2. Methodology Overview

The AtmoSync analytical workflow follows these stages:

```text
Raw Telemetry
     ↓
Data Validation
     ↓
Data Cleaning
     ↓
Feature Engineering
     ↓
Hourly Aggregation
     ↓
Exploratory Data Analysis
     ↓
Anomaly Detection
     ↓
Micro-Climate Comparison
     ↓
Arbitrage Analytics
     ↓
Visualization
```

---

## 3. Data Collection

Telemetry data represents environmental observations collected from monitored environments.

The initial dataset may be generated using an IoT simulator when physical sensors are not available.

### Example Data Fields

| Field | Description |
|---|---|
| `container_id` | Identifier of the monitored environment |
| `timestamp` | Date and time of the observation |
| `temperature_c` | Temperature in Celsius |
| `humidity_pct` | Relative humidity percentage |
| `ping_status` | Device communication status |

---

## 4. Data Validation

Before analysis, incoming data is checked for quality.

Validation checks include:

- Required columns exist
- Timestamps are valid
- Temperature values are numeric
- Humidity values are numeric
- Container identifiers are present
- Duplicate records are identified
- Missing values are measured
- Invalid environmental values are flagged

Example validation logic:

```text
Check schema
     ↓
Check data types
     ↓
Check missing values
     ↓
Check duplicates
     ↓
Check value ranges
     ↓
Approve / Flag records
```

---

## 5. Data Cleaning

The cleaning stage prepares telemetry for analytical use.

### 5.1 Missing Values

Missing values are identified before analysis.

Depending on the field and analytical requirement, missing observations may be:

- Removed
- Replaced using an appropriate method
- Forward-filled for selected time-series use cases
- Retained and flagged

No imputation method should be applied automatically without considering the meaning of the variable.

### 5.2 Duplicate Records

Duplicate telemetry events are detected using a suitable combination of identifiers and timestamps.

Potential duplicate records are removed or flagged to prevent double-counting.

### 5.3 Data Types

The following standardizations are applied:

```text
timestamp       → datetime
temperature_c   → numeric
humidity_pct    → numeric
container_id    → categorical/string
ping_status     → categorical
```

---

## 6. Feature Engineering

Additional analytical features can be derived from the cleaned telemetry.

### Temperature Features

```text
temperature_range
temperature_change
rolling_temperature_average
temperature_deviation
```

### Humidity Features

```text
humidity_change
rolling_humidity_average
humidity_deviation
```

### Time Features

```text
date
hour
day
day_of_week
```

These features support time-series and comparative analysis.

---

## 7. Hourly Aggregation

Raw telemetry is aggregated into hourly metrics.

For each monitored environment and hour, the system calculates:

```text
PING_COUNT
AVG_TEMP_C
PEAK_TEMP_C
MIN_TEMP_C
AVG_HUMIDITY_PCT
```

### Example

Suppose an environment has several temperature readings during one hour:

```text
24°C
25°C
26°C
25°C
```

Then:

```text
Average Temperature = 25°C
Peak Temperature    = 26°C
Minimum Temperature = 24°C
```

This reduces high-frequency telemetry into an easier-to-analyze analytical dataset.

---

## 8. Exploratory Data Analysis

Exploratory Data Analysis (EDA) is performed to understand the structure and behavior of the data.

EDA includes:

- Descriptive statistics
- Distribution analysis
- Time-series analysis
- Correlation analysis
- Environment-level comparisons
- Temperature trends
- Humidity trends

### Example Questions

- What is the average temperature?
- What is the temperature range?
- Which environment has the highest average humidity?
- At what times are temperature changes largest?
- Are temperature and humidity moving together?

---

## 9. Micro-Climate Comparison

The project compares environmental conditions between monitored environments.

For two environments A and B:

```text
Temperature Difference =
Temperature(A) - Temperature(B)
```

and:

```text
Humidity Difference =
Humidity(A) - Humidity(B)
```

These differences are analyzed over time rather than relying on a single observation.

---

## 10. Anomaly Detection

An anomaly is an observation that differs substantially from the expected pattern.

AtmoSync can use multiple approaches.

### 10.1 Threshold-Based Detection

A domain-specific threshold can be used:

```text
IF temperature > configured_threshold
THEN flag anomaly
```

Thresholds should be defined according to the specific operating environment.

### 10.2 Z-Score

For a variable with mean `μ` and standard deviation `σ`:

```text
Z = (x - μ) / σ
```

Large absolute z-scores may indicate unusual observations.

### 10.3 Interquartile Range

The interquartile range is:

```text
IQR = Q3 - Q1
```

Potential outliers can be identified using:

```text
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

### 10.4 Isolation Forest

For larger datasets, Isolation Forest can be evaluated as an unsupervised anomaly-detection method.

---

## 11. Micro-Climate Arbitrage Analytics

The project defines micro-climate arbitrage as the analytical comparison of environmental differences that may have operational significance.

For example:

```text
Environment A
Temperature = 23°C
Humidity    = 52%

Environment B
Temperature = 29°C
Humidity    = 70%
```

The analytical differences are:

```text
Temperature Difference = 6°C
Humidity Difference    = 18 percentage points
```

The system can flag this difference for further investigation.

### Important Interpretation

A detected difference is an **analytical opportunity indicator**, not proof of a financial arbitrage opportunity.

Additional factors may be required before an operational or financial decision is made.

---

## 12. Opportunity Indicator

A configurable opportunity indicator can combine environmental differences.

A simple conceptual structure is:

```text
Opportunity Indicator =
Weighted Temperature Difference
+
Weighted Humidity Difference
+
Anomaly Signal
```

The weights should be determined from the project's business requirements.

The indicator should be treated as a configurable analytical feature rather than a universal financial metric.

---

## 13. Time-Series Analysis

Environmental variables are analyzed across time.

Common analyses include:

- Hour-over-hour change
- Daily averages
- Rolling averages
- Peak periods
- Stable periods
- Sudden environmental changes

Example:

```text
Hour 1 → 24°C
Hour 2 → 24.5°C
Hour 3 → 26°C
Hour 4 → 29°C
```

The increasing pattern can be investigated as a potential environmental shift.

---

## 14. Dashboard Methodology

The dashboard should present information in several layers.

### KPI Layer

Suggested KPIs:

- Total Telemetry Records
- Active Environments
- Average Temperature
- Average Humidity
- Anomaly Count
- Opportunity Indicators

### Trend Layer

Charts can display:

- Temperature over time
- Humidity over time
- Temperature differences
- Humidity differences

### Comparison Layer

Users can compare:

- Environment A vs Environment B
- Average temperature
- Average humidity
- Environmental variation

### Alert Layer

Potential anomalies and large environmental differences can be highlighted for investigation.

---

## 15. Data Quality Checks

The project should monitor:

- Row counts
- Null values
- Duplicate records
- Invalid timestamps
- Invalid temperature values
- Invalid humidity values
- Unexpected container IDs
- Missing hourly periods

These checks help maintain confidence in analytical results.

---

## 16. Reproducibility

The methodology is designed to be reproducible.

Key practices include:

- Version-controlled source code
- Documented transformations
- Consistent data schemas
- Parameterized analytical thresholds
- Separate raw and processed data
- Reusable Python functions
- dbt-based transformations

---

## 17. Final Analytical Process

```text
Collect Telemetry
       ↓
Validate Data
       ↓
Clean Data
       ↓
Create Features
       ↓
Aggregate Hourly Metrics
       ↓
Explore Data
       ↓
Detect Anomalies
       ↓
Compare Micro-Climates
       ↓
Calculate Opportunity Indicators
       ↓
Build Dashboard
       ↓
Generate Insights
```

---

## 18. Methodology Outcome

The methodology enables AtmoSync to transform raw IoT telemetry into a structured analytical workflow that supports:

- Micro-climate monitoring
- Environmental comparison
- Anomaly identification
- Time-series analysis
- Opportunity investigation
- Data-driven visualization
