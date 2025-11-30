pub mod astar;
pub mod bfs;
pub mod dfs;
pub mod idastar;
pub mod iterative_deepening;

use crate::benchmarking::Metrics;

pub trait SearchAlgorithm {
    fn search<P: Problem>(&self, problem: &P) -> SearchResult;
    fn name(&self) -> &str;
}

#[derive(Debug, Clone)]
pub struct SearchResult {
    pub solution: Option<Vec<usize>>,
    pub metrics: Metrics,
    pub success: bool,
}

pub trait Problem: Clone {
    type State: Clone + Eq + std::hash::Hash;
    fn initial_state(&self) -> Self::State;
    fn is_goal(&self, state: &Self::State) -> bool;
    fn successors(&self, state: &Self::State) -> Vec<(Self::State, usize)>;
    fn description(&self) -> String;
    fn heuristic(&self, state: &Self::State) -> usize {
        let _ = state;
        0
    }
}

#[derive(Clone, Debug)]
pub struct Node<S> {
    pub state: S,
    pub parent: Option<Box<Node<S>>>,
    pub action: Option<usize>,
    pub path_cost: usize,
    pub depth: usize,
}

impl<S: Clone> Node<S> {
    pub fn new(state: S) -> Self {
        Node {
            state,
            parent: None,
            action: None,
            path_cost: 0,
            depth: 0,
        }
    }

    pub fn child(&self, state: S, action: usize, step_cost: usize) -> Self {
        Node {
            state,
            parent: Some(Box::new(self.clone())),
            action: Some(action),
            path_cost: self.path_cost + step_cost,
            depth: self.depth + 1,
        }
    }

    pub fn extract_solution(&self) -> Vec<usize> {
        let mut actions = Vec::new();
        let mut current = Some(self);

        while let Some(node) = current {
            if let Some(action) = node.action {
                actions.push(action);
            }
            current = node.parent.as_ref().map(|p| p.as_ref());
        }

        actions.reverse();
        actions
    }
}
