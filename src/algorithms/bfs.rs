use super::{Node, Problem, SearchAlgorithm, SearchResult};
use crate::benchmarking::{Metrics, SharedMetrics};
use std::collections::{HashSet, VecDeque};
use std::time::Instant;

pub struct BFS;

impl SearchAlgorithm for BFS {
    fn search<P: Problem>(&self, problem: &P) -> SearchResult {
        let start = Instant::now();
        let mut metrics = Metrics::default();

        let initial_node = Node::new(problem.initial_state());
        let mut frontier = VecDeque::new();
        frontier.push_back(initial_node);

        let mut explored = HashSet::new();
        metrics.nodes_generated = 1;

        while let Some(node) = frontier.pop_front() {
            metrics.nodes_visited += 1;

            if problem.is_goal(&node.state) {
                let solution = node.extract_solution();
                metrics.solution_length = solution.len();
                metrics.time_ms = start.elapsed().as_millis() as f64;
                metrics.memory_kb =
                    (explored.len() + frontier.len()) * std::mem::size_of::<P::State>() / 1024;

                return SearchResult {
                    solution: Some(solution),
                    metrics,
                    status: 0, // Succès
                };
            }

            explored.insert(node.state.clone());

            for (successor_state, cost) in problem.successors(&node.state) {
                if !explored.contains(&successor_state)
                    && !frontier.iter().any(|n| n.state == successor_state)
                {
                    let child = node.child(successor_state, metrics.nodes_generated, cost);
                    frontier.push_back(child);
                    metrics.nodes_generated += 1;
                }
            }

            metrics.max_frontier_size = metrics.max_frontier_size.max(frontier.len());
        }

        metrics.time_ms = start.elapsed().as_millis() as f64;
        metrics.memory_kb = explored.len() * std::mem::size_of::<P::State>() / 1024;

        SearchResult {
            solution: None,
            metrics,
            status: 2, // Pas de solution
        }
    }

    fn search_with_shared_metrics<P: Problem>(&self, problem: &P, shared: SharedMetrics) -> SearchResult {
        let initial_node = Node::new(problem.initial_state());
        let mut frontier = VecDeque::new();
        frontier.push_back(initial_node);

        let mut explored = HashSet::new();
        shared.update(|m| m.nodes_generated = 1);

        while let Some(node) = frontier.pop_front() {
            shared.increment_visited();

            if problem.is_goal(&node.state) {
                let solution = node.extract_solution();
                shared.set_solution_length(solution.len());
                shared.set_memory_kb(
                    (explored.len() + frontier.len()) * std::mem::size_of::<P::State>() / 1024,
                );

                return SearchResult {
                    solution: Some(solution),
                    metrics: shared.get(),
                    status: 0, // Succès
                };
            }

            explored.insert(node.state.clone());

            for (successor_state, cost) in problem.successors(&node.state) {
                if !explored.contains(&successor_state)
                    && !frontier.iter().any(|n| n.state == successor_state)
                {
                    let generated = shared.get().nodes_generated;
                    let child = node.child(successor_state, generated, cost);
                    frontier.push_back(child);
                    shared.increment_generated();
                }
            }

            shared.update_max_frontier(frontier.len());
        }

        shared.set_memory_kb(explored.len() * std::mem::size_of::<P::State>() / 1024);

        SearchResult {
            solution: None,
            metrics: shared.get(),
            status: 2, // Pas de solution
        }
    }

    fn name(&self) -> &str {
        "BFS"
    }
}
