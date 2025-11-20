use serde::{Serialize, Deserialize};

/// Métriques de performance pour un algorithme de recherche
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct Metrics {
    /// Temps d'exécution en millisecondes
    pub time_ms: f64,
    
    /// Mémoire utilisée en Ko
    pub memory_kb: usize,
    
    /// Nombre de nœuds visités
    pub nodes_visited: usize,
    
    /// Nombre de nœuds générés
    pub nodes_generated: usize,
    
    /// Taille maximale de la frontière
    pub max_frontier_size: usize,
    
    /// Longueur de la solution trouvée
    pub solution_length: usize,
}

impl Metrics {
    /// Calcule le facteur de branchement effectif
    pub fn effective_branching_factor(&self) -> f64 {
        if self.solution_length == 0 {
            return 0.0;
        }
        
        // Approximation: b^d ≈ N où N = nodes_generated, d = solution_length
        (self.nodes_generated as f64).powf(1.0 / self.solution_length as f64)
    }
    
    /// Retourne un résumé formaté des métriques
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

/// Résultat d'un benchmark unique
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenchmarkResult {
    pub algorithm: String,
    pub problem: String,
    pub problem_size: usize,
    pub instance_id: usize,
    pub success: bool,
    pub metrics: Metrics,
    pub timestamp: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub initial_state: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

/// Résultats agrégés de plusieurs benchmarks
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
    /// Calcule les résultats agrégés à partir d'un ensemble de résultats
    pub fn from_results(results: &[BenchmarkResult]) -> Self {
        let total = results.len();
        let successful = results.iter().filter(|r| r.success).count();
        
        let successful_results: Vec<_> = results.iter()
            .filter(|r| r.success)
            .collect();
        
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
            avg_time_ms: successful_results.iter().map(|r| r.metrics.time_ms).sum::<f64>() / n,
            avg_memory_kb: successful_results.iter().map(|r| r.metrics.memory_kb).sum::<usize>() as f64 / n,
            avg_nodes_visited: successful_results.iter().map(|r| r.metrics.nodes_visited).sum::<usize>() as f64 / n,
            avg_nodes_generated: successful_results.iter().map(|r| r.metrics.nodes_generated).sum::<usize>() as f64 / n,
            avg_solution_length: successful_results.iter().map(|r| r.metrics.solution_length).sum::<usize>() as f64 / n,
            avg_ebf: successful_results.iter().map(|r| r.metrics.effective_branching_factor()).sum::<f64>() / n,
        }
    }
}
