import * as aq from "https://cdn.jsdelivr.net/npm/arquero@5.4.1/+esm";

function readCsvData(csvContent) {
  return aq.fromCSV(csvContent).rename({ benchmark: "engine", runtime: "benchmark" });
}

function preprocessData(table) {
  return table
    .select(aq.not("run_index", "score"))
    .filter((d) => d.elapsed_time_ns !== 0 && d.return_code === 0)
    .select(aq.not("return_code"));
}

function addBenchmarkScores(table) {
  // Calculate geometric mean per benchmark: exp(mean(ln(x)))
  const benchmarkStats = table
    .groupby("benchmark")
    .rollup({ gmean_elapsed_ns: (d) => op.exp(op.mean(op.log(d.elapsed_time_ns))) });

  // Join and calculate speedup score
  return table
    .join(benchmarkStats, "benchmark")
    .derive({ score: (d) => d.gmean_elapsed_ns / d.elapsed_time_ns })
    .select("engine", "benchmark", "elapsed_time_ns", "score");
}

function getEngineScores(table) {
  return table
    .groupby("engine")
    .rollup({ total_score: (d) => op.sum(d.score) })
    .orderby(aq.desc("total_score"));
}

export function buildTables(csvContent) {
  const raw = readCsvData(csvContent);
  const preprocessed = preprocessData(raw);
  const benchmarks = addBenchmarkScores(preprocessed);
  const engineScores = getEngineScores(benchmarks);

  const engines = engineScores.array("engine");
  const benchmarkNames = [...new Set(benchmarks.array("benchmark"))].sort();

  // Pivot: engine x benchmark scores + total_score
  const scoresPivot = benchmarks
    .groupby("engine")
    .pivot("benchmark", { score: (d) => op.mean(d.score) })
    .join(engineScores, "engine")
    .orderby(aq.desc("total_score"));
  const scoresByBenchmark = scoresPivot.select("engine", ...benchmarkNames, "total_score");

  // Pivot: engine x benchmark times (seconds)
  const timesPivot = benchmarks
    .derive({ elapsed_time_s: (d) => d.elapsed_time_ns / 1000000000 })
    .groupby("engine")
    .pivot("benchmark", { elapsed_time_s: (d) => op.mean(d.elapsed_time_s) });
  const engineRuntimes = benchmarks
    .derive({ elapsed_time_s: (d) => d.elapsed_time_ns / 1000000000 })
    .groupby("engine")
    .rollup({ total_runtime: (d) => op.sum(d.elapsed_time_s) });
  // Reorder to match engine score ranking
  const runtimesByBenchmark = aq
    .table({ engine: engines })
    .join(timesPivot, "engine")
    .join(engineRuntimes, "engine")
    .select("engine", ...benchmarkNames, "total_runtime");

  return { raw, benchmarks, engines, engineScores, scores: scoresByBenchmark, runtimes: runtimesByBenchmark };
}
