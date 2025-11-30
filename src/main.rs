use clap::Parser;
use std::fs;
use std::time::Instant;

mod algorithms;
mod benchmarking;
mod problems;
mod utils;

use benchmarking::{BenchmarkConfig, BenchmarkRunner};

#[derive(Parser, Debug)]
#[command(author, version, about = "Benchmarking d'algorithmes de recherche", long_about = None)]
struct Args {
    #[arg(short, long, default_value = "all")]
    algorithm: String,

    #[arg(short, long, default_value = "all")]
    problem: String,

    #[arg(short, long, default_value = "3")]
    size: usize,

    #[arg(short, long, default_value = "10")]
    iterations: usize,

    #[arg(short, long, default_value = "results/benchmark_results.json")]
    output: String,

    #[arg(short = 't', long, default_value = "0")]
    threads: usize,

    #[arg(long, default_value = "60")]
    timeout: u64,
}

fn main() {
    let args = Args::parse();

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
