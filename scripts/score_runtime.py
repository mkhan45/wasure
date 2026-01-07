import polars as pl
from pathlib import Path


def read_csv_data(filepath: str) -> pl.DataFrame:
    """Read CSV file and return polars DataFrame."""
    results_path = Path(__file__).parent.parent / "wasure" / "results" / filepath
    return pl.read_csv(results_path).rename(
        {"benchmark": "engine", "runtime": "benchmark"}
    )


def preprocess_data(df: pl.DataFrame) -> pl.DataFrame:
    """Remove invalid rows and unnecessary columns."""
    return (
        df.drop(["run_index", "score"])
        .filter((pl.col("elapsed_time_ns") != 0) & (pl.col("return_code") == 0))
        .drop(["return_code"])
    )


def add_benchmark_scores(df: pl.DataFrame) -> pl.DataFrame:
    """Add speedup-based scores relative to geometric mean of each benchmark."""
    # Calculate geometric mean for each benchmark
    # Geometric mean = exp(mean(ln(x)))
    benchmark_stats = df.group_by("benchmark").agg(
        [pl.col("elapsed_time_ns").log().mean().exp().alias("gmean_elapsed_ns")]
    )

    # Join stats back and calculate speedup
    df_with_stats = df.join(benchmark_stats, on="benchmark")

    # Speedup = gmean / engine_time
    df_with_stats = df_with_stats.with_columns(
        [(pl.col("gmean_elapsed_ns") / pl.col("elapsed_time_ns")).alias("score")]
    )

    # Keep only original columns plus score
    return df_with_stats.select(["engine", "benchmark", "elapsed_time_ns", "score"])


def get_engine_scores(df: pl.DataFrame) -> pl.DataFrame:
    """Get total score for each engine across all benchmarks."""
    return (
        df.group_by("engine")
        .agg(pl.col("score").sum().alias("total_score"))
        .sort("total_score", descending=True)
    )


def process_runtime_data(df: pl.DataFrame) -> pl.DataFrame:
    """Process and analyze runtime data."""
    return (
        df.with_columns(
            [
                (pl.col("elapsed_time_ns") / 1_000_000_000).alias("elapsed_time_s"),
            ]
        )
        .drop(["elapsed_time_ns"])
        .sort(["engine", "benchmark"])
    )


if __name__ == "__main__":
    df = read_csv_data("cmu-pc.csv")

    df = preprocess_data(df)
    print("Preprocessed data:")
    print(df)
    print("\n" + "=" * 80 + "\n")

    df = add_benchmark_scores(df)
    print("Data with benchmark scores (speedup relative to geometric mean):")
    print(df)
    print("\n" + "=" * 80 + "\n")

    print("Engine Scores (ranked by total score):")
    engine_scores = get_engine_scores(df)
    print(engine_scores)
    print("\n" + "=" * 80 + "\n")

    # Get engine order by total score (for consistent column ordering)
    engine_order = engine_scores["engine"].to_list()

    # Table 1: Engine / Score by benchmark / Total score
    print("Engine Scores by Benchmark:")
    scores_pivot = (
        df.pivot(on="benchmark", index="engine", values="score")
        .join(engine_scores, on="engine")
        .sort("total_score", descending=True)
    )
    # Reorder columns: engine, benchmark scores (sorted), total_score
    benchmark_cols = sorted(
        [c for c in scores_pivot.columns if c not in ["engine", "total_score"]]
    )
    scores_pivot = scores_pivot.select(["engine"] + benchmark_cols + ["total_score"])
    print(scores_pivot)
    print("\n" + "=" * 80 + "\n")

    # Table 2: Engine / Time by benchmark (seconds)
    print("Engine Runtimes by Benchmark (seconds):")
    times_pivot = df.with_columns(
        (pl.col("elapsed_time_ns") / 1_000_000_000).alias("elapsed_time_s")
    ).pivot(on="benchmark", index="engine", values="elapsed_time_s")
    # Reorder to match engine score ranking
    times_pivot = pl.DataFrame({"engine": engine_order}).join(
        times_pivot, on="engine", how="left"
    )
    # Reorder columns: engine, then benchmark columns (sorted)
    benchmark_cols = sorted([c for c in times_pivot.columns if c != "engine"])
    times_pivot = times_pivot.select(["engine"] + benchmark_cols)
    print(times_pivot)
    print("\n" + "=" * 80 + "\n")
