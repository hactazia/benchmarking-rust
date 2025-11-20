use crate::algorithms::Problem;
use rand::Rng;
use std::collections::HashMap;

/// Problème du plus court chemin dans un graphe
#[derive(Clone)]
pub struct ShortestPath {
    graph: HashMap<usize, Vec<(usize, usize)>>,
    start: usize,
    goal: usize,
    heuristic_values: HashMap<usize, usize>,
    seed: Option<u64>,
}

impl ShortestPath {
    /// Retourne l'état initial sous forme de chaîne formatée
    pub fn initial_state_string(&self) -> String {
        if let Some(seed) = self.seed {
            format!("Seed: {}", seed)
        } else {
            format!("Start: {} -> Goal: {}", self.start, self.goal)
        }
    }
    
    pub fn new(start: usize, goal: usize) -> Self {
        ShortestPath {
            graph: HashMap::new(),
            start,
            goal,
            heuristic_values: HashMap::new(),
            seed: None,
        }
    }
    
    /// Ajoute une arête dans le graphe
    pub fn add_edge(&mut self, from: usize, to: usize, cost: usize) {
        self.graph.entry(from).or_insert_with(Vec::new).push((to, cost));
    }
    
    /// Définit la valeur heuristique pour un nœud
    pub fn set_heuristic(&mut self, node: usize, value: usize) {
        self.heuristic_values.insert(node, value);
    }
    
    /// Génère un graphe en grille
    pub fn generate_grid(width: usize, height: usize) -> Self {
        let start = 0;
        let goal = width * height - 1;
        let mut graph = ShortestPath::new(start, goal);
        
        for row in 0..height {
            for col in 0..width {
                let current = row * width + col;
                
                // Droite
                if col < width - 1 {
                    graph.add_edge(current, current + 1, 1);
                }
                
                // Bas
                if row < height - 1 {
                    graph.add_edge(current, current + width, 1);
                }
                
                // Gauche
                if col > 0 {
                    graph.add_edge(current, current - 1, 1);
                }
                
                // Haut
                if row > 0 {
                    graph.add_edge(current, current - width, 1);
                }
                
                // Heuristique: distance de Manhattan jusqu'au but
                let goal_row = goal / width;
                let goal_col = goal % width;
                let h = row.abs_diff(goal_row) + col.abs_diff(goal_col);
                graph.set_heuristic(current, h);
            }
        }
        
        graph
    }
    
    /// Génère un graphe aléatoire
    pub fn generate_random(nodes: usize, edges: usize, start: usize, goal: usize) -> Self {
        Self::generate_random_with_seed(nodes, edges, start, goal, None)
    }
    
    /// Génère un graphe aléatoire avec une seed spécifique
    pub fn generate_random_with_seed(nodes: usize, edges: usize, start: usize, goal: usize, seed: Option<u64>) -> Self {
        use rand::SeedableRng;
        
        let mut graph = ShortestPath::new(start, goal);
        graph.seed = seed;
        
        let mut rng: Box<dyn rand::RngCore> = if let Some(s) = seed {
            Box::new(rand::rngs::StdRng::seed_from_u64(s))
        } else {
            Box::new(rand::thread_rng())
        };
        
        for _ in 0..edges {
            let from = rng.gen_range(0..nodes);
            let to = rng.gen_range(0..nodes);
            let cost = rng.gen_range(1..10);
            
            if from != to {
                graph.add_edge(from, to, cost);
            }
        }
        
        // Heuristique aléatoire (sous-estimation)
        for node in 0..nodes {
            let h = if node == goal {
                0
            } else {
                rng.gen_range(0..20)
            };
            graph.set_heuristic(node, h);
        }
        
        graph
    }
}

impl Problem for ShortestPath {
    type State = usize;
    
    fn initial_state(&self) -> Self::State {
        self.start
    }
    
    fn is_goal(&self, state: &Self::State) -> bool {
        *state == self.goal
    }
    
    fn successors(&self, state: &Self::State) -> Vec<(Self::State, usize)> {
        self.graph
            .get(state)
            .cloned()
            .unwrap_or_default()
    }
    
    fn heuristic(&self, state: &Self::State) -> usize {
        *self.heuristic_values.get(state).unwrap_or(&0)
    }
    
    fn description(&self) -> String {
        format!("Plus court chemin: {} nœuds, de {} à {}", 
                self.graph.len(), self.start, self.goal)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_grid_graph() {
        let graph = ShortestPath::generate_grid(3, 3);
        assert_eq!(graph.start, 0);
        assert_eq!(graph.goal, 8);
    }
    
    #[test]
    fn test_successors() {
        let graph = ShortestPath::generate_grid(3, 3);
        let successors = graph.successors(&4); // Centre de la grille
        assert_eq!(successors.len(), 4);
    }
}
