import polars as pl
from pathlib import Path


def read_csv_data(filepath: str) -> pl.DataFrame:
    """Read CSV file and return polars DataFrame."""
    results_path = Path(__file__).parent.parent / "wasure" / "results" / filepath
    return pl.read_csv(results_path).rename({'benchmark': 'engine', 'runtime': 'benchmark'})


def preprocess_data(df: pl.DataFrame) -> pl.DataFrame:
    """Remove invalid rows and unnecessary columns."""
    return (
        df
        .drop(['run_index', 'score'])
        .filter(
            (pl.col('elapsed_time_ns') != 0) &
            (pl.col('return_code') == 0)
        )
        .drop(['return_code'])
    )


def add_benchmark_scores(df: pl.DataFrame) -> pl.DataFrame:
    """Add speedup-based scores relative to geometric mean of each benchmark."""
    # Calculate geometric mean for each benchmark
    # Geometric mean = exp(mean(ln(x)))
    benchmark_stats = (
        df
        .group_by('benchmark')
        .agg([
            pl.col('elapsed_time_ns').log().mean().exp().alias('gmean_elapsed_ns')
        ])
    )
    
    # Join stats back and calculate speedup
    df_with_stats = df.join(benchmark_stats, on='benchmark')
    
    # Speedup = gmean / engine_time
    df_with_stats = df_with_stats.with_columns([
        (pl.col('gmean_elapsed_ns') / pl.col('elapsed_time_ns')).alias('score')
    ])
    
    # Keep only original columns plus score
    return df_with_stats.select(['engine', 'benchmark', 'elapsed_time_ns', 'score'])


def get_engine_scores(df: pl.DataFrame) -> pl.DataFrame:
    """Get total score for each engine across all benchmarks."""
    return (
        df
        .group_by('engine')
        .agg(pl.col('score').sum().alias('total_score'))
        .sort('total_score', descending=True)
    )


def process_runtime_data(df: pl.DataFrame) -> pl.DataFrame:
    """Process and analyze runtime data."""
    return (
        df
        .with_columns([
            (pl.col('elapsed_time_ns') / 1_000_000_000).alias('elapsed_time_s'),
        ])
        .drop(['elapsed_time_ns'])
        .sort(['engine', 'benchmark'])
    )


if __name__ == '__main__':
    df = read_csv_data('cmu-pc.csv')
    
    df = preprocess_data(df)
    print("Preprocessed data:")
    print(df)
    print("\n" + "="*80 + "\n")
    
    df = add_benchmark_scores(df)
    print("Data with benchmark scores (speedup relative to geometric mean):")
    print(df)
    print("\n" + "="*80 + "\n")
    
    print("Engine Scores (ranked by total score):")
    engine_scores = get_engine_scores(df)
    print(engine_scores)
    print("\n" + "="*80 + "\n")
