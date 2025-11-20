#!/bin/bash

# Script Bash pour exécuter une suite complète de benchmarks

echo -e "\033[36mBenchmarking\033[0m"
echo -e "\033[36m============\033[0m"
echo ""

# Vérifier que Cargo est installé
if ! command -v cargo &> /dev/null; then
    echo -e "\033[31mErreur: Cargo n'est pas installé\033[0m"
    echo -e "\033[33m   Installez Rust depuis: https://rustup.rs/\033[0m"
    exit 1
fi

# Compiler le projet
echo -e "\033[33mCompilation du projet en mode release...\033[0m"
cargo build --release
if [ $? -ne 0 ]; then
    echo -e "\033[31mErreur de compilation\033[0m"
    exit 1
fi
echo -e "\033[32mCompilation réussie\n\033[0m"

# Benchmark 1: Taquin 3x3
echo -e "\033[36mBenchmark 1a: Taquin 3x3 (20 instances)\033[0m"
cargo run --release -- --problem taquin --size 3 --iterations 20 --output results/taquin_3x3.json
echo ""

echo -e "\033[36mBenchmark 1b: Taquin 4x4 (5 instances)\033[0m"
cargo run --release -- --problem taquin --size 4 --iterations 5 --output results/taquin_4x4.json
echo ""

# Benchmark 2: Plus court chemin (multiples tailles)
echo -e "\033[36mBenchmark 2a: Plus Court Chemin 10x10 (10 instances)\033[0m"
cargo run --release -- --problem shortest-path --size 10 --iterations 10 --output results/shortest_path_10.json
echo ""

echo -e "\033[36mBenchmark 2b: Plus Court Chemin 100x100 (10 instances)\033[0m"
cargo run --release -- --problem shortest-path --size 100 --iterations 10 --output results/shortest_path_100.json
echo ""

echo -e "\033[36mBenchmark 2c: Plus Court Chemin 1000x1000 (5 instances)\033[0m"
cargo run --release -- --problem shortest-path --size 1000 --iterations 5 --output results/shortest_path_1000.json
echo ""

# Benchmark 3: Graphes aléatoires
echo -e "\033[36mBenchmark 3a: Graphe Aléatoire 50 noeuds (10 instances)\033[0m"
cargo run --release -- --problem shortest-path-random --size 50 --iterations 10 --output results/shortest_path_random_50.json
echo ""

echo -e "\033[36mBenchmark 3b: Graphe Aléatoire 200 noeuds (10 instances)\033[0m"
cargo run --release -- --problem shortest-path-random --size 200 --iterations 10 --output results/shortest_path_random_200.json
echo ""

echo -e "\033[36mBenchmark 3c: Graphe Aléatoire 500 noeuds (5 instances)\033[0m"
cargo run --release -- --problem shortest-path-random --size 500 --iterations 5 --output results/shortest_path_random_500.json
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "\033[33mPython n'est pas installé, impossible de générer les visualisations et les rapports\033[0m"
    echo -e "\033[33m   Installez Python 3.8+ pour continuer\033[0m"
    exit 0
fi

# Utiliser python3 si disponible, sinon python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Vérifier les dépendances Python
echo -e "\033[33mVérification des dépendances Python...\033[0m"
$PYTHON_CMD -m pip install -r requirements.txt --quiet
echo -e "\033[32mDépendances installées\n\033[0m"

# Générer les visualisations pour chaque benchmark
echo -e "\033[36mFusion des résultats...\033[0m"
$PYTHON_CMD analysis/merge_results.py results/shortest_path.json results/shortest_path_10.json results/shortest_path_100.json results/shortest_path_1000.json
$PYTHON_CMD analysis/merge_results.py results/shortest_path_random.json results/shortest_path_random_50.json results/shortest_path_random_200.json results/shortest_path_random_500.json
$PYTHON_CMD analysis/merge_results.py results/taquin.json results/taquin_3x3.json results/taquin_4x4.json
$PYTHON_CMD analysis/merge_results.py results/all.json results/taquin.json results/shortest_path.json results/shortest_path_random.json

echo ""

echo -e "\033[36mGénération des visualisations...\033[0m"

$PYTHON_CMD analysis/visualize.py results/

echo ""

# Générer les rapports
echo -e "\033[36mGénération des rapports...\033[0m"

$PYTHON_CMD analysis/generate_report.py results/

echo ""
echo -e "\033[32mTous les benchmarks sont terminés!\033[0m"
echo -e "\033[36m  Résultats JSON : results/*.json\033[0m"
echo -e "\033[36m  Visualisations : results/visuals/\033[0m"
echo -e "\033[36m  Rapports       : results/reports/\033[0m"
