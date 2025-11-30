use super::dfs::DFS;
use super::{Problem, SearchAlgorithm, SearchResult};
use crate::benchmarking::{Metrics, SharedMetrics};
use std::time::Instant;

pub struct IterativeDeepening {
    pub max_depth: usize,
}

impl IterativeDeepening {
    pub fn new(max_depth: usize) -> Self {
        IterativeDeepening { max_depth }
    }
}

impl SearchAlgorithm for IterativeDeepening {
    fn search<P: Problem>(&self, problem: &P) -> SearchResult {
        let start = Instant::now();
        let mut total_metrics = Metrics::default();

        for depth in 0..=self.max_depth {
            let dfs = DFS::with_max_depth(depth);
            let result = dfs.search(problem);

            total_metrics.nodes_visited += result.metrics.nodes_visited;
            total_metrics.nodes_generated += result.metrics.nodes_generated;
            total_metrics.max_frontier_size = total_metrics
                .max_frontier_size
                .max(result.metrics.max_frontier_size);

            if result.status == 0 {
                total_metrics.solution_length = result.metrics.solution_length;
                total_metrics.time_ms = start.elapsed().as_millis() as f64;
                total_metrics.memory_kb = result.metrics.memory_kb;

                return SearchResult {
                    solution: result.solution,
                    metrics: total_metrics,
                    status: 0, // Succès
                };
            }
        }

        total_metrics.time_ms = start.elapsed().as_millis() as f64;

        SearchResult {
            solution: None,
            metrics: total_metrics,
            status: 2, // Pas de solution
        }
    }

    fn search_with_shared_metrics<P: Problem>(&self, problem: &P, shared: SharedMetrics) -> SearchResult {
        for depth in 0..=self.max_depth {
            let dfs = DFS::with_max_depth(depth);
            // On utilise la version partagée du DFS pour avoir les métriques mises à jour
            let result = dfs.search_with_shared_metrics(problem, shared.clone());

            if result.status == 0 {
                return SearchResult {
                    solution: result.solution,
                    metrics: shared.get(),
                    status: 0, // Succès
                };
            }
        }

        SearchResult {
            solution: None,
            metrics: shared.get(),
            status: 2, // Pas de solution
        }
    }

    fn name(&self) -> &str {
        "Iterative Deepening"
    }
}
