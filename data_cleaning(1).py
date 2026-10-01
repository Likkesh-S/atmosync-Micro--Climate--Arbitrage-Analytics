"""
AtmoSync: Micro-Climate Arbitrage Analytics
File: src/data_cleaning.py

Purpose:
    Provide reusable data-cleaning and quality-check functions for
    micro-climate telemetry.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "container_id",
    "timestamp",
    "temperature_c",
    "humidity_pct",
    "ping_status",
}


def validate_required_columns(df: pd.DataFrame) -> None:
    """Raise an error if required telemetry columns are missing."""
    missing = REQUIRED_COLUMNS.difference(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert telemetry fields to appropriate data types."""
    data = df.copy()

    data["container_id"] = (
        data["container_id"]
        .astype("string")
        .str.strip()
    )

    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce",
        utc=True,
    )

    data["temperature_c"] = pd.to_numeric(
        data["temperature_c"],
        errors="coerce",
    )

    data["humidity_pct"] = pd.to_numeric(
        data["humidity_pct"],
        errors="coerce",
    )

    data["ping_status"] = (
        data["ping_status"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    return data


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate telemetry records."""
    return df.drop_duplicates().reset_index(drop=True)


def handle_missing_values(
    df: pd.DataFrame,
    drop_required: bool = True,
) -> pd.DataFrame:
    """Handle missing values in required telemetry fields.

    By default, records missing identifiers, timestamps, temperature,
    or humidity are removed. Ping status is retained when missing because
    it can be separately investigated as a data-quality issue.
    """
    data = df.copy()

    required_measurements = [
        "container_id",
        "timestamp",
        "temperature_c",
        "humidity_pct",
    ]

    if drop_required:
        data = data.dropna(
            subset=required_measurements
        )

    return data.reset_index(drop=True)


def flag_invalid_ranges(
    df: pd.DataFrame,
    min_temperature_c: float = -50.0,
    max_temperature_c: float = 80.0,
    min_humidity_pct: float = 0.0,
    max_humidity_pct: float = 100.0,
) -> pd.DataFrame:
    """Flag values outside configured validation ranges.

    These are data-quality ranges, not universal operating limits.
    Adjust them according to the actual sensor and project context.
    """
    data = df.copy()

    data["temperature_range_flag"] = (
        (data["temperature_c"] < min_temperature_c)
        | (data["temperature_c"] > max_temperature_c)
    )

    data["humidity_range_flag"] = (
        (data["humidity_pct"] < min_humidity_pct)
        | (data["humidity_pct"] > max_humidity_pct)
    )

    data["quality_flag"] = (
        data["temperature_range_flag"]
        | data["humidity_range_flag"]
    )

    return data


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add commonly used time-series features."""
    data = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(data["timestamp"]):
        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce",
            utc=True,
        )

    data["date"] = data["timestamp"].dt.date
    data["hour"] = data["timestamp"].dt.hour
    data["day_of_week"] = data["timestamp"].dt.dayofweek
    data["day_name"] = data["timestamp"].dt.day_name()

    return data


def clean_telemetry(
    df: pd.DataFrame,
    drop_invalid_ranges: bool = False,
) -> pd.DataFrame:
    """Run the complete telemetry cleaning workflow.

    Invalid range values are flagged by default rather than removed.
    This preserves potentially useful records for investigation.
    """
    validate_required_columns(df)

    data = convert_data_types(df)
    data = remove_duplicates(data)
    data = handle_missing_values(data)
    data = flag_invalid_ranges(data)
    data = add_time_features(data)

    if drop_invalid_ranges:
        data = data.loc[
            ~data["quality_flag"]
        ].copy()

    return data.reset_index(drop=True)


def generate_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Generate a compact data-quality report."""
    validate_required_columns(df)

    report = pd.DataFrame(
        {
            "metric": [
                "row_count",
                "duplicate_rows",
                "missing_container_id",
                "missing_timestamp",
                "missing_temperature",
                "missing_humidity",
                "missing_ping_status",
            ],
            "value": [
                len(df),
                int(df.duplicated().sum()),
                int(df["container_id"].isna().sum()),
                int(df["timestamp"].isna().sum()),
                int(df["temperature_c"].isna().sum()),
                int(df["humidity_pct"].isna().sum()),
                int(df["ping_status"].isna().sum()),
            ],
        }
    )

    return report


def save_cleaned_data(
    df: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """Save cleaned telemetry data to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)

    return path


if __name__ == "__main__":
    from data_ingestion import generate_sample_telemetry

    telemetry = generate_sample_telemetry(
        rows_per_container=24,
        containers=[
            "CONTAINER_A",
            "CONTAINER_B",
            "CONTAINER_C",
        ],
    )

    cleaned = clean_telemetry(telemetry)

    report = generate_quality_report(telemetry)

    output = save_cleaned_data(
        cleaned,
        "data/processed/cleaned_telemetry.csv",
    )

    print(f"Cleaned records: {len(cleaned)}")
    print(f"Saved cleaned data to: {output}")
    print("\nData quality report:")
    print(report.to_string(index=False))
