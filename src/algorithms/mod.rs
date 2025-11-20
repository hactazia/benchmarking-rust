pub mod bfs;
pub mod dfs;
pub mod iterative_deepening;
pub mod astar;
pub mod idastar;

use crate::benchmarking::Metrics;

/// Trait pour tous les algorithmes de recherche
pub trait SearchAlgorithm {
    /// Execute l'algorithme de recherche
    fn search<P: Problem>(&self, problem: &P) -> SearchResult;
    
    /// Retourne le nom de l'algorithme
    fn name(&self) -> &str;
}

/// Résultat d'une recherche
#[derive(Debug, Clone)]
pub struct SearchResult {
    /// Solution trouvée (chemin d'actions)
    pub solution: Option<Vec<usize>>,
    /// Métriques de performance
    pub metrics: Metrics,
    /// Succès de la recherche
    pub success: bool,
}

/// Trait pour définir un problème de recherche
pub trait Problem: Clone {
    /// Type représentant un état du problème
    type State: Clone + Eq + std::hash::Hash;
    
    /// État initial
    fn initial_state(&self) -> Self::State;
    
    /// Test si un état est un état but
    fn is_goal(&self, state: &Self::State) -> bool;
    
    /// Retourne les états successeurs d'un état donné
    fn successors(&self, state: &Self::State) -> Vec<(Self::State, usize)>;
    
    /// Heuristique pour les algorithmes informés (0 par défaut)
    fn heuristic(&self, state: &Self::State) -> usize {
        let _ = state;
        0
    }
    
    /// Retourne une description du problème
    fn description(&self) -> String;
}

/// Noeud pour les algorithmes de recherche
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
