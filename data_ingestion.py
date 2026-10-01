"""
AtmoSync: Micro-Climate Arbitrage Analytics
File: src/data_ingestion.py

Purpose:
    Generate, load, and validate micro-climate telemetry data for the
    AtmoSync analytics pipeline.

The functions in this module are intentionally reusable so they can work
with both simulated CSV data and future sensor/streaming integrations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "container_id",
    "timestamp",
    "temperature_c",
    "humidity_pct",
    "ping_status",
}


def validate_schema(df: pd.DataFrame) -> None:
    """Validate that the telemetry DataFrame contains required columns.

    Raises:
        ValueError: If one or more required columns are missing.
    """
    missing = REQUIRED_COLUMNS.difference(df.columns)

    if missing:
        raise ValueError(
            f"Missing required telemetry columns: {sorted(missing)}"
        )


def prepare_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize telemetry data.

    The function:
        - validates the input schema
        - converts timestamps to UTC-aware datetimes
        - converts numeric measurements
        - normalizes ping status
        - removes exact duplicate rows
        - sorts the result chronologically

    Returns:
        A cleaned copy of the telemetry DataFrame.
    """
    validate_schema(df)

    data = df.copy()

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

    data["container_id"] = data["container_id"].astype("string").str.strip()

    data["ping_status"] = (
        data["ping_status"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    data = data.drop_duplicates()

    data = data.dropna(
        subset=[
            "container_id",
            "timestamp",
            "temperature_c",
            "humidity_pct",
        ]
    )

    data = data.sort_values(
        by=["container_id", "timestamp"]
    ).reset_index(drop=True)

    return data


def load_telemetry_csv(file_path: str | Path) -> pd.DataFrame:
    """Load telemetry data from a CSV file and prepare it for analysis."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Telemetry file not found: {path}")

    df = pd.read_csv(path)
    return prepare_telemetry(df)


def generate_sample_telemetry(
    rows_per_container: int = 24,
    containers: Optional[Iterable[str]] = None,
    start_time: str = "2026-01-01 00:00:00",
    seed: int = 42,
) -> pd.DataFrame:
    """Generate reproducible sample micro-climate telemetry.

    This simulator is useful for local development and notebook testing
    when a live IoT source is unavailable.

    Args:
        rows_per_container: Number of hourly observations per container.
        containers: Iterable of container/environment IDs.
        start_time: Starting timestamp.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame containing simulated telemetry.
    """
    if rows_per_container <= 0:
        raise ValueError("rows_per_container must be greater than zero.")

    if containers is None:
        containers = ["CONTAINER_A", "CONTAINER_B", "CONTAINER_C"]

    containers = list(containers)

    if not containers:
        raise ValueError("At least one container is required.")

    rng = np.random.default_rng(seed)

    timestamps = pd.date_range(
        start=start_time,
        periods=rows_per_container,
        freq="h",
        tz="UTC",
    )

    records = []

    # Small baseline differences represent different micro-climates.
    temperature_offsets = np.linspace(-1.5, 2.0, len(containers))
    humidity_offsets = np.linspace(-5.0, 7.0, len(containers))

    for index, container_id in enumerate(containers):
        for hour_index, timestamp in enumerate(timestamps):
            daily_cycle = np.sin(
                (2 * np.pi * hour_index) / 24
            )

            temperature = (
                26.0
                + 3.0 * daily_cycle
                + temperature_offsets[index]
                + rng.normal(0, 0.6)
            )

            humidity = (
                62.0
                - 8.0 * daily_cycle
                + humidity_offsets[index]
                + rng.normal(0, 2.0)
            )

            humidity = float(np.clip(humidity, 20, 95))

            ping_status = (
                "OK"
                if rng.random() >= 0.02
                else "FAILED"
            )

            records.append(
                {
                    "container_id": container_id,
                    "timestamp": timestamp,
                    "temperature_c": round(float(temperature), 2),
                    "humidity_pct": round(float(humidity), 2),
                    "ping_status": ping_status,
                }
            )

    return prepare_telemetry(pd.DataFrame(records))


def save_telemetry_csv(
    df: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """Validate and save telemetry data as a CSV file."""
    validate_schema(df)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)

    return path


if __name__ == "__main__":
    # Example local execution:
    # python src/data_ingestion.py

    sample = generate_sample_telemetry(
        rows_per_container=24,
        containers=[
            "CONTAINER_A",
            "CONTAINER_B",
            "CONTAINER_C",
        ],
    )

    output = save_telemetry_csv(
        sample,
        "data/processed/sample_telemetry.csv",
    )

    print(f"Generated {len(sample)} telemetry records.")
    print(f"Saved telemetry dataset to: {output}")
    print("\nSample records:")
    print(sample.head())
