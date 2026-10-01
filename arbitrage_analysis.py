"""
AtmoSync - Micro-Climate Arbitrage Analysis Module

Compares environmental conditions across containers/locations and identifies
relative micro-climate opportunities using configurable thresholds.

This module is designed for analytics and decision-support. It does not
execute trades or financial transactions.
"""

from pathlib import Path

import numpy as np
import pandas as pd


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    """Validate that required columns exist."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def prepare_hourly_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate telemetry into container-hour metrics.

    Expected columns:
    - container_id
    - timestamp
    - temperature_c
    - humidity_pct
    """
    validate_columns(
        df,
        ["container_id", "timestamp", "temperature_c", "humidity_pct"],
    )

    result = df.copy()
    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")

    hourly = (
        result.groupby(
            [
                "container_id",
                pd.Grouper(key="timestamp", freq="h"),
            ],
            as_index=False,
        )
        .agg(
            avg_temperature_c=("temperature_c", "mean"),
            peak_temperature_c=("temperature_c", "max"),
            min_temperature_c=("temperature_c", "min"),
            avg_humidity_pct=("humidity_pct", "mean"),
            ping_count=("container_id", "size"),
        )
    )

    return hourly


def calculate_market_metrics(
    hourly_df: pd.DataFrame,
    target_temperature_c: float = 22.0,
    target_humidity_pct: float = 50.0,
) -> pd.DataFrame:
    """
    Calculate environmental deviation and stability metrics.

    Lower deviation means the observed micro-climate is closer to the
    configured target conditions.
    """
    result = hourly_df.copy()

    validate_columns(
        result,
        [
            "container_id",
            "timestamp",
            "avg_temperature_c",
            "avg_humidity_pct",
        ],
    )

    result["temperature_deviation_c"] = (
        result["avg_temperature_c"] - target_temperature_c
    ).abs()

    result["humidity_deviation_pct_points"] = (
        result["avg_humidity_pct"] - target_humidity_pct
    ).abs()

    if "peak_temperature_c" in result.columns and "min_temperature_c" in result.columns:
        result["temperature_range_c"] = (
            result["peak_temperature_c"] - result["min_temperature_c"]
        )
    else:
        result["temperature_range_c"] = np.nan

    return result


def compare_microclimates(hourly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare containers within each hour.

    The container with the lowest temperature/humidity deviation from the
    configured targets receives a relative rank of 1 for that metric.
    """
    result = hourly_df.copy()

    validate_columns(
        result,
        [
            "container_id",
            "timestamp",
            "temperature_deviation_c",
            "humidity_deviation_pct_points",
        ],
    )

    result["temperature_rank"] = (
        result.groupby("timestamp")["temperature_deviation_c"]
        .rank(method="min", ascending=True)
    )

    result["humidity_rank"] = (
        result.groupby("timestamp")["humidity_deviation_pct_points"]
        .rank(method="min", ascending=True)
    )

    result["environmental_score"] = (
        1
        / (
            1
            + result["temperature_deviation_c"]
            + result["humidity_deviation_pct_points"]
        )
    ).round(4)

    return result


def calculate_arbitrage_opportunities(
    comparison_df: pd.DataFrame,
    temperature_spread_threshold_c: float = 3.0,
    humidity_spread_threshold_pct: float = 10.0,
) -> pd.DataFrame:
    """
    Identify relative environmental spreads between containers.

    An opportunity is flagged when the hourly spread between the highest
    and lowest observed values reaches the configured thresholds.

    This is an analytical indicator, not a financial trading signal.
    """
    result = comparison_df.copy()

    validate_columns(
        result,
        [
            "timestamp",
            "avg_temperature_c",
            "avg_humidity_pct",
        ],
    )

    grouped = result.groupby("timestamp")

    result["hourly_temperature_spread_c"] = grouped[
        "avg_temperature_c"
    ].transform(lambda s: s.max() - s.min())

    result["hourly_humidity_spread_pct"] = grouped[
        "avg_humidity_pct"
    ].transform(lambda s: s.max() - s.min())

    result["temperature_spread_opportunity"] = (
        result["hourly_temperature_spread_c"]
        >= temperature_spread_threshold_c
    ).astype(int)

    result["humidity_spread_opportunity"] = (
        result["hourly_humidity_spread_pct"]
        >= humidity_spread_threshold_pct
    ).astype(int)

    result["arbitrage_opportunity"] = (
        (result["temperature_spread_opportunity"] == 1)
        | (result["humidity_spread_opportunity"] == 1)
    ).astype(int)

    result["opportunity_strength"] = (
        result["hourly_temperature_spread_c"]
        / max(temperature_spread_threshold_c, 0.001)
        + result["hourly_humidity_spread_pct"]
        / max(humidity_spread_threshold_pct, 0.001)
    ).round(2)

    return result


def generate_opportunity_summary(
    opportunity_df: pd.DataFrame,
) -> pd.DataFrame:
    """Generate a container-level summary of opportunity indicators."""
    validate_columns(
        opportunity_df,
        [
            "container_id",
            "arbitrage_opportunity",
            "environmental_score",
        ],
    )

    summary = (
        opportunity_df.groupby("container_id")
        .agg(
            observations=("container_id", "size"),
            opportunity_hours=("arbitrage_opportunity", "sum"),
            average_environmental_score=("environmental_score", "mean"),
            average_temperature_c=("avg_temperature_c", "mean"),
            average_humidity_pct=("avg_humidity_pct", "mean"),
        )
        .reset_index()
    )

    summary["opportunity_rate_pct"] = (
        summary["opportunity_hours"] / summary["observations"] * 100
    ).round(2)

    summary["average_environmental_score"] = summary[
        "average_environmental_score"
    ].round(4)

    return summary


def run_arbitrage_analysis(
    df: pd.DataFrame,
    target_temperature_c: float = 22.0,
    target_humidity_pct: float = 50.0,
    temperature_spread_threshold_c: float = 3.0,
    humidity_spread_threshold_pct: float = 10.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run the complete AtmoSync micro-climate arbitrage analysis."""
    hourly = prepare_hourly_data(df)

    metrics = calculate_market_metrics(
        hourly,
        target_temperature_c=target_temperature_c,
        target_humidity_pct=target_humidity_pct,
    )

    comparison = compare_microclimates(metrics)

    opportunities = calculate_arbitrage_opportunities(
        comparison,
        temperature_spread_threshold_c=temperature_spread_threshold_c,
        humidity_spread_threshold_pct=humidity_spread_threshold_pct,
    )

    summary = generate_opportunity_summary(opportunities)

    return opportunities, summary


def save_arbitrage_results(
    opportunities: pd.DataFrame,
    summary: pd.DataFrame,
    results_path: str = "data/processed/arbitrage_opportunities.csv",
    summary_path: str = "data/processed/arbitrage_summary.csv",
) -> None:
    """Save detailed opportunities and summary outputs."""
    results_file = Path(results_path)
    summary_file = Path(summary_path)

    results_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.parent.mkdir(parents=True, exist_ok=True)

    opportunities.to_csv(results_file, index=False)
    summary.to_csv(summary_file, index=False)


if __name__ == "__main__":
    from data_ingestion import generate_sample_telemetry

    telemetry = generate_sample_telemetry(
        containers=["CONTAINER_A", "CONTAINER_B", "CONTAINER_C"],
        periods=24,
        seed=42,
    )

    opportunities, summary = run_arbitrage_analysis(
        telemetry,
        target_temperature_c=22.0,
        target_humidity_pct=50.0,
        temperature_spread_threshold_c=3.0,
        humidity_spread_threshold_pct=10.0,
    )

    print("Micro-climate arbitrage analysis completed.")
    print(f"Hourly records analyzed: {len(opportunities)}")
    print(
        "Opportunity records: "
        f"{opportunities['arbitrage_opportunity'].sum()}"
    )

    print("\nOpportunity summary:")
    print(summary.to_string(index=False))

    save_arbitrage_results(opportunities, summary)

    print("\nSaved detailed results to:")
    print("data/processed/arbitrage_opportunities.csv")
    print("Saved summary to:")
    print("data/processed/arbitrage_summary.csv")
