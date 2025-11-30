use super::{Node, Problem, SearchAlgorithm, SearchResult};
use crate::benchmarking::{Metrics, SharedMetrics};
use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};
use std::time::Instant;

#[derive(Clone)]
struct AStarNode<S> {
    node: Node<S>,
    f_score: usize,
}

impl<S> PartialEq for AStarNode<S> {
    fn eq(&self, other: &Self) -> bool {
        self.f_score == other.f_score
    }
}

impl<S> Eq for AStarNode<S> {}

impl<S> PartialOrd for AStarNode<S> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl<S> Ord for AStarNode<S> {
    fn cmp(&self, other: &Self) -> Ordering {
        other.f_score.cmp(&self.f_score)
    }
}

pub struct AStar;

impl SearchAlgorithm for AStar {
    fn search<P: Problem>(&self, problem: &P) -> SearchResult {
        let start = Instant::now();
        let mut metrics = Metrics::default();

        let initial_state = problem.initial_state();
        let initial_h = problem.heuristic(&initial_state);
        let initial_node = Node::new(initial_state.clone());

        let mut frontier = BinaryHeap::new();
        frontier.push(AStarNode {
            node: initial_node,
            f_score: initial_h,
        });

        let mut explored = HashMap::new();
        let mut g_scores = HashMap::new();
        g_scores.insert(initial_state, 0);

        metrics.nodes_generated = 1;

        while let Some(astar_node) = frontier.pop() {
            let node = astar_node.node;
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
                    status: 0,
                };
            }

            if explored.contains_key(&node.state) {
                continue;
            }

            explored.insert(node.state.clone(), node.path_cost);

            for (successor_state, cost) in problem.successors(&node.state) {
                let tentative_g = node.path_cost + cost;

                if let Some(&existing_g) = g_scores.get(&successor_state) {
                    if tentative_g >= existing_g {
                        continue;
                    }
                }

                g_scores.insert(successor_state.clone(), tentative_g);
                let h = problem.heuristic(&successor_state);
                let f = tentative_g + h;

                let child = node.child(successor_state, metrics.nodes_generated, cost);
                frontier.push(AStarNode {
                    node: child,
                    f_score: f,
                });
                metrics.nodes_generated += 1;
            }

            metrics.max_frontier_size = metrics.max_frontier_size.max(frontier.len());
        }

        metrics.time_ms = start.elapsed().as_millis() as f64;
        metrics.memory_kb = explored.len() * std::mem::size_of::<P::State>() / 1024;

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
        let initial_h = problem.heuristic(&initial_state);
        let initial_node = Node::new(initial_state.clone());

        let mut frontier = BinaryHeap::new();
        frontier.push(AStarNode {
            node: initial_node,
            f_score: initial_h,
        });

        let mut explored = HashMap::new();
        let mut g_scores = HashMap::new();
        g_scores.insert(initial_state, 0);

        shared.update(|m| m.nodes_generated = 1);

        while let Some(astar_node) = frontier.pop() {
            let node = astar_node.node;
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
                    status: 0,
                };
            }

            if explored.contains_key(&node.state) {
                continue;
            }

            explored.insert(node.state.clone(), node.path_cost);

            for (successor_state, cost) in problem.successors(&node.state) {
                let tentative_g = node.path_cost + cost;

                if let Some(&existing_g) = g_scores.get(&successor_state) {
                    if tentative_g >= existing_g {
                        continue;
                    }
                }

                g_scores.insert(successor_state.clone(), tentative_g);
                let h = problem.heuristic(&successor_state);
                let f = tentative_g + h;

                let generated = shared.get().nodes_generated;
                let child = node.child(successor_state, generated, cost);
                frontier.push(AStarNode {
                    node: child,
                    f_score: f,
                });
                shared.increment_generated();
            }

            shared.update_max_frontier(frontier.len());
        }

        shared.set_memory_kb(explored.len() * std::mem::size_of::<P::State>() / 1024);

        SearchResult {
            solution: None,
            metrics: shared.get(),
            status: 2,
        }
    }

    fn name(&self) -> &str {
        "A*"
    }
}
