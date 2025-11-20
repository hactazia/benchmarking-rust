use clap::Parser;
use std::fs;
use std::time::Instant;

mod algorithms;
mod benchmarking;
mod problems;
mod utils;

use benchmarking::{BenchmarkRunner, BenchmarkConfig};

#[derive(Parser, Debug)]
#[command(author, version, about = "Benchmarking d'algorithmes de recherche", long_about = None)]
struct Args {
    /// Algorithme à utiliser (all, bfs, dfs, id, astar, idastar)
    #[arg(short, long, default_value = "all")]
    algorithm: String,

    /// Problème à résoudre (all, taquin, shortest-path, shortest-path-random)
    #[arg(short, long, default_value = "all")]
    problem: String,

    /// Taille du problème (pour le taquin: 3, 4, 5)
    #[arg(short, long, default_value = "3")]
    size: usize,

    /// Nombre d'instances à tester
    #[arg(short, long, default_value = "10")]
    iterations: usize,

    /// Fichier de sortie pour les résultats
    #[arg(short, long, default_value = "results/benchmark_results.json")]
    output: String,

    /// Nombre de threads (0 = auto-détection)
    #[arg(short = 't', long, default_value = "0")]
    threads: usize,

    /// Timeout par algorithme en secondes (0 = pas de timeout)
    #[arg(long, default_value = "60")]
    timeout: u64,
}

fn main() {
    let args = Args::parse();

    // Configurer le nombre de threads
    let num_threads = if args.threads == 0 {
        num_cpus::get()
    } else {
        args.threads
    };
    
    rayon::ThreadPoolBuilder::new()
        .num_threads(num_threads)
        .build_global()
        .unwrap();

    println!("Détails du benchmark:");
    println!("  Algorithme: {}", args.algorithm);
    println!("  Problème: {}", args.problem);
    println!("  Taille: {}", args.size);
    println!("  Itérations: {}", args.iterations);
    println!("  Threads: {}", num_threads);
    println!("  Timeout: {}sec", args.timeout);
    println!();

    // Créer le dossier de résultats s'il n'existe pas
    fs::create_dir_all("results").expect("Impossible de créer le dossier results");

    let config = BenchmarkConfig {
        algorithm: args.algorithm.clone(),
        problem: args.problem.clone(),
        size: args.size,
        iterations: args.iterations,
        output_file: args.output.clone(),
        threads: num_threads,
        timeout_secs: args.timeout,
    };

    let start = Instant::now();
    let runner = BenchmarkRunner::new(config);
    
    match runner.run() {
        Ok(_) => {
            let duration = start.elapsed();
            println!("\nBenchmarks terminés");
            println!("  Temps total: {:.2?}", duration);
            println!("  Résultats sauvegardés dans {}", args.output);
        }
        Err(e) => {
            eprintln!("\nErreur lors du benchmark: {}", e);
            std::process::exit(1);
        }
    }
}
