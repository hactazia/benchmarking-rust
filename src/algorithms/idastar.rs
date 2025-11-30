use super::{Node, Problem, SearchAlgorithm, SearchResult};
use crate::benchmarking::{Metrics, SharedMetrics};
use std::collections::HashSet;
use std::time::Instant;

pub struct IDAStar {
    pub max_bound: usize,
}

impl IDAStar {
    pub fn new(max_bound: usize) -> Self {
        IDAStar { max_bound }
    }

    fn search_recursive<P: Problem>(
        &self,
        problem: &P,
        node: &Node<P::State>,
        bound: usize,
        explored: &mut HashSet<P::State>,
        metrics: &mut Metrics,
    ) -> (Option<Vec<usize>>, usize) {
        metrics.nodes_visited += 1;

        let f = node.path_cost + problem.heuristic(&node.state);

        if f > bound {
            return (None, f);
        }

        if problem.is_goal(&node.state) {
            return (Some(node.extract_solution()), 0);
        }

        explored.insert(node.state.clone());

        let mut min_bound = usize::MAX;

        for (successor_state, cost) in problem.successors(&node.state) {
            if explored.contains(&successor_state) {
                continue;
            }

            let child = node.child(successor_state, metrics.nodes_generated, cost);
            metrics.nodes_generated += 1;

            let (result, new_bound) =
                self.search_recursive(problem, &child, bound, explored, metrics);

            if result.is_some() {
                explored.remove(&node.state);
                return (result, 0);
            }

            if new_bound < min_bound {
                min_bound = new_bound;
            }
        }

        explored.remove(&node.state);
        (None, min_bound)
    }

    fn search_recursive_shared<P: Problem>(
        &self,
        problem: &P,
        node: &Node<P::State>,
        bound: usize,
        explored: &mut HashSet<P::State>,
        shared: &SharedMetrics,
    ) -> (Option<Vec<usize>>, usize) {
        shared.increment_visited();

        let f = node.path_cost + problem.heuristic(&node.state);

        if f > bound {
            return (None, f);
        }

        if problem.is_goal(&node.state) {
            return (Some(node.extract_solution()), 0);
        }

        explored.insert(node.state.clone());

        let mut min_bound = usize::MAX;

        for (successor_state, cost) in problem.successors(&node.state) {
            if explored.contains(&successor_state) {
                continue;
            }

            let generated = shared.get().nodes_generated;
            let child = node.child(successor_state, generated, cost);
            shared.increment_generated();

            let (result, new_bound) =
                self.search_recursive_shared(problem, &child, bound, explored, shared);

            if result.is_some() {
                explored.remove(&node.state);
                return (result, 0);
            }

            if new_bound < min_bound {
                min_bound = new_bound;
            }
        }

        explored.remove(&node.state);
        (None, min_bound)
    }
}

impl SearchAlgorithm for IDAStar {
    fn search<P: Problem>(&self, problem: &P) -> SearchResult {
        let start = Instant::now();
        let mut metrics = Metrics::default();

        let initial_state = problem.initial_state();
        let mut bound = problem.heuristic(&initial_state);
        let initial_node = Node::new(initial_state);

        metrics.nodes_generated = 1;

        loop {
            let mut explored = HashSet::new();
            let (result, new_bound) =
                self.search_recursive(problem, &initial_node, bound, &mut explored, &mut metrics);

            if let Some(solution) = result {
                metrics.solution_length = solution.len();
                metrics.time_ms = start.elapsed().as_millis() as f64;
                metrics.memory_kb = explored.len() * std::mem::size_of::<P::State>() / 1024;

                return SearchResult {
                    solution: Some(solution),
                    metrics,
                    status: 0,
                };
            }

            if new_bound == usize::MAX || bound >= self.max_bound {
                break;
            }

            bound = new_bound;
        }

        metrics.time_ms = start.elapsed().as_millis() as f64;

        SearchResult {
            solution: None,
            metrics,
            status: 2,
        }
    }

    fn search_with_shared_metrics<P: Problem>(
        &self,
        problem: &P,
        shared: SharedMetrics,
    ) -> SearchResult {
        let initial_state = problem.initial_state();
        let mut bound = problem.heuristic(&initial_state);
        let initial_node = Node::new(initial_state);

        shared.update(|m| m.nodes_generated = 1);

        loop {
            let mut explored = HashSet::new();
            let (result, new_bound) =
                self.search_recursive_shared(problem, &initial_node, bound, &mut explored, &shared);

            if let Some(solution) = result {
                shared.set_solution_length(solution.len());
                shared.set_memory_kb(explored.len() * std::mem::size_of::<P::State>() / 1024);

                return SearchResult {
                    solution: Some(solution),
                    metrics: shared.get(),
                    status: 0,
                };
            }

            if new_bound == usize::MAX || bound >= self.max_bound {
                break;
            }

            bound = new_bound;
        }

        SearchResult {
            solution: None,
            metrics: shared.get(),
            status: 2,
        }
    }

    fn name(&self) -> &str {
        "IDA*"
    }
}
