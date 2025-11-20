use super::metrics::{BenchmarkResult, AggregatedResults};
use crate::algorithms::*;
use crate::problems::*;
use serde_json;
use std::fs::File;
use std::io::Write;
use rayon::prelude::*;
use std::time::Duration;
use std::sync::mpsc::{channel, RecvTimeoutError};
use std::sync::Arc;

pub struct BenchmarkConfig {
    pub algorithm: String,
    pub problem: String,
    pub size: usize,
    pub iterations: usize,
    pub output_file: String,
    pub threads: usize,
    pub timeout_secs: u64,
}

pub struct BenchmarkRunner {
    config: BenchmarkConfig,
}

impl BenchmarkRunner {
    pub fn new(config: BenchmarkConfig) -> Self {
        BenchmarkRunner { config }
    }
    
    /// Obtenir les noms d'algorithmes en fonction du type de problème
    fn get_algorithm_names(&self, for_taquin: bool) -> Result<Vec<&str>, String> {
        match self.config.algorithm.as_str() {
            "all" => {
                if for_taquin {
                    Ok(vec!["BFS", "DFS", "ID", "A*-Manhattan", "IDA*-Manhattan"])
                } else {
                    Ok(vec!["BFS", "DFS", "ID", "A*", "IDA*"])
                }
            }
            "bfs" => Ok(vec!["BFS"]),
            "dfs" => Ok(vec!["DFS"]),
            "id" => Ok(vec!["ID"]),
            "astar" => {
                if for_taquin {
                    Ok(vec!["A*-Manhattan"])
                } else {
                    Ok(vec!["A*"])
                }
            }
            "idastar" => {
                if for_taquin {
                    Ok(vec!["IDA*-Manhattan"])
                } else {
                    Ok(vec!["IDA*"])
                }
            }
            _ => Err(format!("Algorithme inconnu: {}", self.config.algorithm)),
        }
    }
    
    /// Exécute un algorithme avec timeout
    fn execute_with_timeout<P: Problem + Clone + Send + 'static>(
        &self,
        problem: &P,
        algo_name: &str,
        timeout_duration: Duration,
    ) -> (SearchResult, Option<String>) {
        if self.config.timeout_secs > 0 {
            let (tx, rx) = channel();
            let problem_clone = problem.clone();
            let algo = algo_name.to_string();
            
            std::thread::spawn(move || {
                let res = Self::execute_algorithm(&algo, &problem_clone);
                let _ = tx.send(res);
            });
            
            match rx.recv_timeout(timeout_duration) {
                Ok(res) => (res, None),
                Err(RecvTimeoutError::Timeout) => {
                    (
                        SearchResult {
                            solution: None,
                            metrics: crate::benchmarking::Metrics::default(),
                            success: false,
                        },
                        Some(format!("Timeout après {} secondes", self.config.timeout_secs))
                    )
                }
                Err(_) => {
                    (
                        SearchResult {
                            solution: None,
                            metrics: crate::benchmarking::Metrics::default(),
                            success: false,
                        },
                        Some("Erreur de communication".to_string())
                    )
                }
            }
        } else {
            (Self::execute_algorithm(algo_name, problem), None)
        }
    }
    
    /// Exécute un algorithme spécifique
    fn execute_algorithm<P: Problem>(algo_name: &str, problem: &P) -> SearchResult {
        match algo_name {
            "BFS" => bfs::BFS.search(problem),
            "DFS" => dfs::DFS::with_max_depth(50).search(problem),
            "ID" => iterative_deepening::IterativeDeepening::new(50).search(problem),
            "A*-Manhattan" | "A*" => astar::AStar.search(problem),
            "IDA*-Manhattan" | "IDA*" => idastar::IDAStar::new(100).search(problem),
            _ => SearchResult {
                solution: None,
                metrics: crate::benchmarking::Metrics::default(),
                success: false,
            },
        }
    }
    
    /// Exécute les benchmarks et génère les résultats
    fn execute_benchmarks<P, F, G>(
        &self,
        algorithm_names: Vec<&str>,
        problem_generator: F,
        problem_name_fn: Arc<dyn Fn(usize) -> String + Send + Sync>,
        initial_state_formatter: G,
    ) -> Result<Vec<BenchmarkResult>, Box<dyn std::error::Error>>
    where
        P: Problem + Clone + Send + Sync + 'static,
        P::State: Send,
        F: Fn(usize) -> P + Send + Sync + Clone,
        G: Fn(&P) -> String + Send + Sync,
    {
        // Créer toutes les tâches
        let all_tasks: Vec<_> = algorithm_names.iter()
            .flat_map(|algo_name| {
                let gen = problem_generator.clone();
                (0..self.config.iterations).map(move |instance_id| {
                    let problem = gen(instance_id);
                    (instance_id, problem, *algo_name)
                })
            })
            .collect();
        
        println!("\nExécution de {} tâches en parallèle sur {} threads...\n", 
                 all_tasks.len(), self.config.threads);
        
        let timeout_duration = Duration::from_secs(self.config.timeout_secs);
        let problem_name = problem_name_fn;
        
        // Exécuter en parallèle
        let results: Vec<BenchmarkResult> = all_tasks
            .par_iter()
            .filter_map(|(instance_id, problem, algo_name)| {
                println!("  Instance {}\t {}/{}\t Démarrage...", 
                    algo_name, instance_id + 1, self.config.iterations);
                
                let (result, error_msg) = self.execute_with_timeout(problem, algo_name, timeout_duration);
                
                let status = if result.success { "✓" } else { "✗" };
                let summary = if result.success {
                    result.metrics.summary()
                } else if let Some(ref err) = error_msg {
                    err.clone()
                } else {
                    "Pas de solution trouvée".to_string()
                };
                
                println!("  Instance {}\t {}/{}\t {} {}", 
                    algo_name, instance_id + 1, self.config.iterations, status, summary);
                
                let final_error = if !result.success {
                    error_msg.or_else(|| Some("Pas de solution trouvée".to_string()))
                } else {
                    None
                };
                
                Some(BenchmarkResult {
                    algorithm: algo_name.to_string(),
                    problem: problem_name(self.config.size),
                    problem_size: self.config.size,
                    instance_id: *instance_id,
                    success: result.success,
                    metrics: result.metrics,
                    timestamp: chrono::Local::now().to_rfc3339(),
                    initial_state: Some(initial_state_formatter(problem)),
                    error: final_error,
                })
            })
            .collect();
        
        Ok(results)
    }
    
    pub fn run(&self) -> Result<(), Box<dyn std::error::Error>> {
        let mut all_results = Vec::new();
        
        match self.config.problem.as_str() {
            "taquin" | "all" => {
                println!("Benchmarking Taquin {}x{}", self.config.size, self.config.size);
                let taquin_results = self.benchmark_taquin()?;
                all_results.extend(taquin_results);
            }
            "shortest-path" => {
                println!("Benchmarking Plus Court Chemin (Grille)");
                let path_results = self.benchmark_shortest_path()?;
                all_results.extend(path_results);
            }
            "shortest-path-random" => {
                println!("Benchmarking Plus Court Chemin (Graphe Aléatoire)");
                let path_results = self.benchmark_shortest_path_random()?;
                all_results.extend(path_results);
            }
            _ => {
                return Err(format!("Problème inconnu: {}", self.config.problem).into());
            }
        }
        
        // Sauvegarder tous les résultats
        self.save_results(&all_results)?;
        
        // Afficher les résultats agrégés
        self.print_summary(&all_results);
        
        Ok(())
    }
    
    fn benchmark_taquin(&self) -> Result<Vec<BenchmarkResult>, Box<dyn std::error::Error>> {
        let algorithm_names = self.get_algorithm_names(true)?;
        let size = self.config.size;
        
        let problem_generator = move |_instance_id: usize| {
            let mut problem = Taquin::new(size, taquin::HeuristicType::Manhattan);
            problem.generate_random(size * size * 10);
            problem
        };
        
        self.execute_benchmarks(
            algorithm_names,
            problem_generator,
            Arc::new(move |size| format!("Taquin-{}x{}", size, size)),
            |p: &Taquin| p.initial_state_string()
        )
    }
    
    fn benchmark_shortest_path(&self) -> Result<Vec<BenchmarkResult>, Box<dyn std::error::Error>> {
        let algorithm_names = self.get_algorithm_names(false)?;
        let size = self.config.size;
        
        let problem_generator = move |_instance_id: usize| {
            ShortestPath::generate_grid(size, size)
        };
        
        self.execute_benchmarks(
            algorithm_names,
            problem_generator,
            Arc::new(move |size| format!("ShortestPath-{}x{}", size, size)),
            |p: &ShortestPath| p.initial_state_string()
        )
    }
    
    fn benchmark_shortest_path_random(&self) -> Result<Vec<BenchmarkResult>, Box<dyn std::error::Error>> {
        let algorithm_names = self.get_algorithm_names(false)?;
        let size = self.config.size;
        let nodes = size;
        let edges = nodes * 3;
        
        println!("  Configuration: {} nœuds, ~{} arêtes par graphe\n", nodes, edges);
        
        let problem_generator = move |_instance_id: usize| {
            let timestamp = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos() as u64;
            ShortestPath::generate_random_with_seed(nodes, edges, 0, nodes - 1, Some(timestamp))
        };
        
        self.execute_benchmarks(
            algorithm_names,
            problem_generator,
            Arc::new(move |size| format!("ShortestPath-Random-{}", size)),
            |p: &ShortestPath| p.initial_state_string()
        )
    }
    
    fn save_results(&self, results: &[BenchmarkResult]) -> Result<(), Box<dyn std::error::Error>> {
        let json = serde_json::to_string_pretty(results)?;
        let mut file = File::create(&self.config.output_file)?;
        file.write_all(json.as_bytes())?;
        Ok(())
    }
    
    fn print_summary(&self, results: &[BenchmarkResult]) {
        println!("\nRésumé:");
        
        // Grouper par algorithme et problème
        let mut grouped: std::collections::HashMap<(String, String), Vec<&BenchmarkResult>> = 
            std::collections::HashMap::new();
        
        for result in results {
            let key = (result.algorithm.clone(), result.problem.clone());
            grouped.entry(key).or_insert_with(Vec::new).push(result);
        }
        
        for ((algorithm, problem), group) in grouped {
            let group_vec: Vec<BenchmarkResult> = group.iter().map(|r| (*r).clone()).collect();
            let aggregated = AggregatedResults::from_results(&group_vec);
            
            println!("\n{} sur {}", algorithm, problem);
            println!("  Succès: {}/{}", aggregated.successful_instances, aggregated.total_instances);
            println!("  Temps moyen: {:.2} ms", aggregated.avg_time_ms);
            println!("  Mémoire moyenne: {:.0} Ko", aggregated.avg_memory_kb);
            println!("  Nœuds visités (moy.): {:.0}", aggregated.avg_nodes_visited);
            println!("  Longueur solution (moy.): {:.1}", aggregated.avg_solution_length);
            println!("  EBF moyen: {:.2}", aggregated.avg_ebf);
        }
    }
}
