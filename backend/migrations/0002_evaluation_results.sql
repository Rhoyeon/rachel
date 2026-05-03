CREATE TABLE IF NOT EXISTS evaluation_results (
  run_id TEXT NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value REAL NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (run_id, metric_name)
);

CREATE INDEX IF NOT EXISTS idx_evaluation_results_metric_name
  ON evaluation_results(metric_name);
