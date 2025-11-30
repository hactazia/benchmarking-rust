use super::dfs::DFS;
use super::{Problem, SearchAlgorithm, SearchResult};
use crate::benchmarking::Metrics;
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

            if result.success {
                total_metrics.solution_length = result.metrics.solution_length;
                total_metrics.time_ms = start.elapsed().as_millis() as f64;
                total_metrics.memory_kb = result.metrics.memory_kb;

                return SearchResult {
                    solution: result.solution,
                    metrics: total_metrics,
                    success: true,
                };
            }
        }

        total_metrics.time_ms = start.elapsed().as_millis() as f64;

        SearchResult {
            solution: None,
            metrics: total_metrics,
            success: false,
        }
    }

    fn name(&self) -> &str {
        "Iterative Deepening"
    }
}
