"""
AtmoSync - Anomaly Detection Module

Detects unusual temperature and humidity behavior in IoT telemetry.
The module provides rule-based detection and an optional Isolation Forest
model for unsupervised anomaly detection.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    """Validate that required columns exist."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def add_rule_based_anomalies(
    df: pd.DataFrame,
    temperature_min: float = 0.0,
    temperature_max: float = 50.0,
    humidity_min: float = 0.0,
    humidity_max: float = 100.0,
    temperature_change_threshold: float = 5.0,
    humidity_change_threshold: float = 20.0,
) -> pd.DataFrame:
    """
    Flag telemetry records that exceed configured environmental thresholds.
    """
    result = df.copy()

    validate_columns(
        result,
        ["temperature_c", "humidity_pct"],
    )

    result["temperature_range_anomaly"] = (
        (result["temperature_c"] < temperature_min)
        | (result["temperature_c"] > temperature_max)
    ).astype(int)

    result["humidity_range_anomaly"] = (
        (result["humidity_pct"] < humidity_min)
        | (result["humidity_pct"] > humidity_max)
    ).astype(int)

    if "temperature_change_c" in result.columns:
        result["temperature_change_anomaly"] = (
            result["temperature_change_c"].abs() > temperature_change_threshold
        ).astype(int)
    else:
        result["temperature_change_anomaly"] = 0

    if "humidity_change_pct_points" in result.columns:
        result["humidity_change_anomaly"] = (
            result["humidity_change_pct_points"].abs()
            > humidity_change_threshold
        ).astype(int)
    else:
        result["humidity_change_anomaly"] = 0

    anomaly_columns = [
        "temperature_range_anomaly",
        "humidity_range_anomaly",
        "temperature_change_anomaly",
        "humidity_change_anomaly",
    ]

    result["rule_anomaly_score"] = result[anomaly_columns].sum(axis=1)
    result["rule_based_anomaly"] = (result["rule_anomaly_score"] > 0).astype(int)

    return result


def add_isolation_forest_anomalies(
    df: pd.DataFrame,
    contamination: float = 0.05,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Detect multivariate anomalies using Isolation Forest.

    The model uses available numeric environmental features. Missing values
    are filled with the corresponding column median before training.
    """
    result = df.copy()

    candidate_features = [
        "temperature_c",
        "humidity_pct",
        "temperature_change_c",
        "humidity_change_pct_points",
        "temperature_rolling_mean_3h",
        "humidity_rolling_mean_3h",
    ]

    features = [column for column in candidate_features if column in result.columns]

    if len(features) < 2:
        raise ValueError(
            "At least two numeric environmental features are required "
            "for Isolation Forest detection."
        )

    model_data = result[features].apply(pd.to_numeric, errors="coerce")
    model_data = model_data.fillna(model_data.median()).fillna(0)

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
    )

    predictions = model.fit_predict(model_data)
    scores = model.decision_function(model_data)

    # Isolation Forest returns -1 for anomalies and 1 for normal records.
    result["isolation_forest_anomaly"] = (predictions == -1).astype(int)
    result["isolation_forest_score"] = scores

    return result


def detect_anomalies(
    df: pd.DataFrame,
    use_isolation_forest: bool = True,
) -> pd.DataFrame:
    """Run the complete AtmoSync anomaly detection pipeline."""
    result = add_rule_based_anomalies(df)

    if use_isolation_forest:
        result = add_isolation_forest_anomalies(result)

        result["combined_anomaly"] = (
            (result["rule_based_anomaly"] == 1)
            | (result["isolation_forest_anomaly"] == 1)
        ).astype(int)
    else:
        result["isolation_forest_anomaly"] = 0
        result["isolation_forest_score"] = np.nan
        result["combined_anomaly"] = result["rule_based_anomaly"]

    return result


def generate_anomaly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate an anomaly summary by container."""
    validate_columns(df, ["container_id"])

    if "combined_anomaly" not in df.columns:
        raise ValueError(
            "Run detect_anomalies() before generating the summary."
        )

    summary = (
        df.groupby("container_id")
        .agg(
            total_records=("container_id", "size"),
            anomalies=("combined_anomaly", "sum"),
            average_temperature_c=("temperature_c", "mean"),
            average_humidity_pct=("humidity_pct", "mean"),
        )
        .reset_index()
    )

    summary["anomaly_rate_pct"] = (
        summary["anomalies"] / summary["total_records"] * 100
    ).round(2)

    return summary


def save_anomaly_results(
    df: pd.DataFrame,
    output_path: str = "data/processed/anomaly_results.csv",
) -> None:
    """Save anomaly detection results to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


if __name__ == "__main__":
    from data_ingestion import generate_sample_telemetry
    from data_cleaning import clean_telemetry
    from feature_engineering import engineer_features

    telemetry = generate_sample_telemetry(
        containers=["CONTAINER_A", "CONTAINER_B", "CONTAINER_C"],
        periods=24,
        seed=42,
    )

    cleaned = clean_telemetry(telemetry)
    featured = engineer_features(cleaned)
    anomalies = detect_anomalies(featured)

    summary = generate_anomaly_summary(anomalies)

    print("Anomaly detection completed.")
    print(f"Rows analyzed: {len(anomalies)}")
    print(
        f"Total anomalies detected: "
        f"{anomalies['combined_anomaly'].sum()}"
    )

    print("\nAnomaly summary:")
    print(summary.to_string(index=False))

    save_anomaly_results(anomalies)
    print("\nSaved to: data/processed/anomaly_results.csv")
