"""
AtmoSync - Feature Engineering Module

Creates time, temperature, humidity, and rolling-window features
for IoT telemetry data used by the AtmoSync analytics pipeline.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    """Validate that required columns exist in the input DataFrame."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar and cyclical time features."""
    result = df.copy()

    validate_columns(result, ["timestamp"])

    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")

    result["hour"] = result["timestamp"].dt.hour
    result["day_of_week"] = result["timestamp"].dt.dayofweek
    result["day_name"] = result["timestamp"].dt.day_name()
    result["is_weekend"] = (result["day_of_week"] >= 5).astype(int)

    # Cyclical encoding preserves the relationship between 23:00 and 00:00.
    result["hour_sin"] = np.sin(2 * np.pi * result["hour"] / 24)
    result["hour_cos"] = np.cos(2 * np.pi * result["hour"] / 24)

    return result


def add_temperature_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add temperature change and rolling statistics by container."""
    result = df.copy()

    validate_columns(result, ["container_id", "timestamp", "temperature_c"])

    result = result.sort_values(["container_id", "timestamp"]).reset_index(drop=True)

    grouped_temp = result.groupby("container_id")["temperature_c"]

    result["temperature_change_c"] = grouped_temp.diff()

    result["temperature_rolling_mean_3h"] = (
        result.groupby("container_id")["temperature_c"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    result["temperature_rolling_std_3h"] = (
        result.groupby("container_id")["temperature_c"]
        .transform(lambda s: s.rolling(window=3, min_periods=2).std())
        .fillna(0)
    )

    result["temperature_deviation_c"] = (
        result["temperature_c"] - result["temperature_rolling_mean_3h"]
    )

    return result


def add_humidity_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add humidity change and rolling statistics by container."""
    result = df.copy()

    validate_columns(result, ["container_id", "timestamp", "humidity_pct"])

    result = result.sort_values(["container_id", "timestamp"]).reset_index(drop=True)

    grouped_humidity = result.groupby("container_id")["humidity_pct"]

    result["humidity_change_pct_points"] = grouped_humidity.diff()

    result["humidity_rolling_mean_3h"] = (
        result.groupby("container_id")["humidity_pct"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    result["humidity_rolling_std_3h"] = (
        result.groupby("container_id")["humidity_pct"]
        .transform(lambda s: s.rolling(window=3, min_periods=2).std())
        .fillna(0)
    )

    result["humidity_deviation_pct_points"] = (
        result["humidity_pct"] - result["humidity_rolling_mean_3h"]
    )

    return result


def add_environmental_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add combined environmental indicators."""
    result = df.copy()

    validate_columns(result, ["temperature_c", "humidity_pct"])

    # Simple interaction feature useful for exploratory analytics and ML.
    result["temperature_humidity_interaction"] = (
        result["temperature_c"] * result["humidity_pct"]
    )

    return result


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run the complete AtmoSync feature engineering pipeline."""
    result = df.copy()

    result = add_time_features(result)
    result = add_temperature_features(result)
    result = add_humidity_features(result)
    result = add_environmental_features(result)

    return result


def save_featured_data(
    df: pd.DataFrame,
    output_path: str = "data/processed/featured_telemetry.csv",
) -> None:
    """Save engineered telemetry data to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


if __name__ == "__main__":
    # Demo using the sample generator from the ingestion module.
    from data_ingestion import generate_sample_telemetry

    telemetry = generate_sample_telemetry(
        containers=["CONTAINER_A", "CONTAINER_B", "CONTAINER_C"],
        periods=24,
        seed=42,
    )

    featured = engineer_features(telemetry)

    print("Feature engineering completed.")
    print(f"Rows: {len(featured)}")
    print(f"Columns: {len(featured.columns)}")
    print("\nGenerated features:")
    print(
        [
            "hour",
            "day_of_week",
            "is_weekend",
            "hour_sin",
            "hour_cos",
            "temperature_change_c",
            "temperature_rolling_mean_3h",
            "temperature_rolling_std_3h",
            "temperature_deviation_c",
            "humidity_change_pct_points",
            "humidity_rolling_mean_3h",
            "humidity_rolling_std_3h",
            "humidity_deviation_pct_points",
            "temperature_humidity_interaction",
        ]
    )

    save_featured_data(featured)
    print("\nSaved to: data/processed/featured_telemetry.csv")
