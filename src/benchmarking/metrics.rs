use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::time::Instant;

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct Metrics {
    pub time_ms: f64,
    pub memory_kb: usize,
    pub nodes_visited: usize,
    pub nodes_generated: usize,
    pub max_frontier_size: usize,
    pub solution_length: usize,
}

/// Métriques partagées pour permettre la récupération en cas de timeout
#[derive(Clone)]
pub struct SharedMetrics {
    inner: Arc<Mutex<Metrics>>,
    start: Instant,
}

impl SharedMetrics {
    pub fn new() -> Self {
        SharedMetrics {
            inner: Arc::new(Mutex::new(Metrics::default())),
            start: Instant::now(),
        }
    }

    pub fn update<F>(&self, f: F)
    where
        F: FnOnce(&mut Metrics),
    {
        if let Ok(mut metrics) = self.inner.lock() {
            f(&mut metrics);
            metrics.time_ms = self.start.elapsed().as_millis() as f64;
        }
    }

    pub fn get(&self) -> Metrics {
        self.inner.lock().map(|m| m.clone()).unwrap_or_default()
    }

    pub fn increment_visited(&self) {
        if let Ok(mut metrics) = self.inner.lock() {
            metrics.nodes_visited += 1;
            metrics.time_ms = self.start.elapsed().as_millis() as f64;
        }
    }

    pub fn increment_generated(&self) {
        if let Ok(mut metrics) = self.inner.lock() {
            metrics.nodes_generated += 1;
        }
    }

    pub fn update_max_frontier(&self, size: usize) {
        if let Ok(mut metrics) = self.inner.lock() {
            metrics.max_frontier_size = metrics.max_frontier_size.max(size);
        }
    }

    pub fn set_memory_kb(&self, kb: usize) {
        if let Ok(mut metrics) = self.inner.lock() {
            metrics.memory_kb = kb;
        }
    }

    pub fn set_solution_length(&self, len: usize) {
        if let Ok(mut metrics) = self.inner.lock() {
            metrics.solution_length = len;
        }
    }
}

impl Default for SharedMetrics {
    fn default() -> Self {
        Self::new()
    }
}

impl Metrics {
    pub fn effective_branching_factor(&self) -> f64 {
        if self.solution_length == 0 {
            return 0.0;
        }

        (self.nodes_generated as f64).powf(1.0 / self.solution_length as f64)
    }

    pub fn summary(&self) -> String {
        format!(
            "{:.2}ms\t{:4}Ko\t{:4}v\t{:4}g\t{:4}\t{:.2}",
            self.time_ms,
            self.memory_kb,
            self.nodes_visited,
            self.nodes_generated,
            self.solution_length,
            self.effective_branching_factor()
        )
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenchmarkResult {
    pub algorithm: String,
    pub problem: String,
    pub problem_size: usize,
    pub instance_id: usize,
    /// 0 = succès, 1 = timeout, 2 = pas de solution trouvée
    pub status: u8,
    pub metrics: Metrics,
    pub timestamp: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub initial_state: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AggregatedResults {
    pub algorithm: String,
    pub problem: String,
    pub problem_size: usize,
    pub total_instances: usize,
    pub successful_instances: usize,
    pub avg_time_ms: f64,
    pub avg_memory_kb: f64,
    pub avg_nodes_visited: f64,
    pub avg_nodes_generated: f64,
    pub avg_solution_length: f64,
    pub avg_ebf: f64,
}

impl AggregatedResults {
    pub fn from_results(results: &[BenchmarkResult]) -> Self {
        let total = results.len();
        let successful = results.iter().filter(|r| r.status == 0).count();

        let successful_results: Vec<_> = results.iter().filter(|r| r.status == 0).collect();

        if successful_results.is_empty() {
            return AggregatedResults {
                algorithm: results[0].algorithm.clone(),
                problem: results[0].problem.clone(),
                problem_size: results[0].problem_size,
                total_instances: total,
                successful_instances: 0,
                avg_time_ms: 0.0,
                avg_memory_kb: 0.0,
                avg_nodes_visited: 0.0,
                avg_nodes_generated: 0.0,
                avg_solution_length: 0.0,
                avg_ebf: 0.0,
            };
        }

        let n = successful_results.len() as f64;

        AggregatedResults {
            algorithm: results[0].algorithm.clone(),
            problem: results[0].problem.clone(),
            problem_size: results[0].problem_size,
            total_instances: total,
            successful_instances: successful,
            avg_time_ms: successful_results
                .iter()
                .map(|r| r.metrics.time_ms)
                .sum::<f64>()
                / n,
            avg_memory_kb: successful_results
                .iter()
                .map(|r| r.metrics.memory_kb)
                .sum::<usize>() as f64
                / n,
            avg_nodes_visited: successful_results
                .iter()
                .map(|r| r.metrics.nodes_visited)
                .sum::<usize>() as f64
                / n,
            avg_nodes_generated: successful_results
                .iter()
                .map(|r| r.metrics.nodes_generated)
                .sum::<usize>() as f64
                / n,
            avg_solution_length: successful_results
                .iter()
                .map(|r| r.metrics.solution_length)
                .sum::<usize>() as f64
                / n,
            avg_ebf: successful_results
                .iter()
                .map(|r| r.metrics.effective_branching_factor())
                .sum::<f64>()
                / n,
        }
    }
}
