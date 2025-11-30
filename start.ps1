# Script PowerShell pour exécuter une suite complète de benchmarks

Write-Host "Benchmarking" -ForegroundColor Cyan
Write-Host "============" -ForegroundColor Cyan
Write-Host ""

# Vérifier que Cargo est installé
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "Erreur: Cargo n'est pas installe" -ForegroundColor Red
    Write-Host "   Installez Rust depuis: https://rustup.rs/" -ForegroundColor Yellow
    exit 1
}

# Compiler le projet
Write-Host "Compilation du projet en mode release..." -ForegroundColor Yellow
cargo build --release
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur de compilation" -ForegroundColor Red
    exit 1
}
Write-Host "Compilation reussie`n" -ForegroundColor Green

# Benchmark 1: Taquin 3x3
Write-Host "Benchmark 1a: Taquin 3x3 (20 instances)" -ForegroundColor Cyan
cargo run --release -- --problem taquin --size 3 --iterations 20 --output results/taquin_3x3.json
Write-Host ""

Write-Host "Benchmark 1b: Taquin 4x4 (5 instances)" -ForegroundColor Cyan
cargo run --release -- --problem taquin --size 4 --iterations 5 --output results/taquin_4x4.json
Write-Host ""

# Benchmark 2: Plus court chemin (multiples tailles)
Write-Host "Benchmark 2a: Plus Court Chemin 10x10 (10 instances)" -ForegroundColor Cyan
cargo run --release -- --problem shortest-path --size 10 --iterations 10 --output results/shortest_path_10.json
Write-Host ""

Write-Host "Benchmark 2b: Plus Court Chemin 100x100 (10 instances)" -ForegroundColor Cyan
cargo run --release -- --problem shortest-path --size 100 --iterations 10 --output results/shortest_path_100.json
Write-Host ""

Write-Host "Benchmark 2c: Plus Court Chemin 1000x1000 (5 instances)" -ForegroundColor Cyan
cargo run --release -- --problem shortest-path --size 1000 --iterations 5 --output results/shortest_path_1000.json
Write-Host ""

# Benchmark 3: Graphes aléatoires
Write-Host "Benchmark 3a: Graphe Aleatoire 50 noeuds (10 instances)" -ForegroundColor Cyan
cargo run --release -- --problem shortest-path-random --size 50 --iterations 10 --output results/shortest_path_random_50.json
Write-Host ""

Write-Host "Benchmark 3b: Graphe Aleatoire 200 noeuds (10 instances)" -ForegroundColor Cyan
cargo run --release -- --problem shortest-path-random --size 200 --iterations 10 --output results/shortest_path_random_200.json
Write-Host ""

Write-Host "Benchmark 3c: Graphe Aleatoire 500 noeuds (5 instances)" -ForegroundColor Cyan
cargo run --release -- --problem shortest-path-random --size 500 --iterations 5 --output results/shortest_path_random_500.json
Write-Host ""

# Verifier que Python est installe
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python n'est pas installe, impossible de generer les visualisations et les rapports" -ForegroundColor Yellow
    Write-Host "   Installez Python 3.8+ pour continuer" -ForegroundColor Yellow
    exit 0
}

# Verifier les dependances Python
Write-Host "Verification des dependances Python..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Dependances installees`n" -ForegroundColor Green

# Generer les visualisations pour chaque benchmark
Write-Host "Fusion des resultats..." -ForegroundColor Cyan
python analysis/merge_results.py results/shortest_path.json results/shortest_path_10.json results/shortest_path_100.json results/shortest_path_1000.json
python analysis/merge_results.py results/shortest_path_random.json results/shortest_path_random_50.json results/shortest_path_random_200.json results/shortest_path_random_500.json
python analysis/merge_results.py results/taquin.json results/taquin_3x3.json results/taquin_4x4.json
python analysis/merge_results.py results/all.json results/taquin.json results/shortest_path.json results/shortest_path_random.json

Write-Host ""

Write-Host "Generation des visualisations..." -ForegroundColor Cyan

python analysis/visualize.py results/

Write-Host ""

# Generer les rapports
Write-Host "Generation des rapports..." -ForegroundColor Cyan

python analysis/generate_report.py results/

Write-Host ""

Write-Host "Generation du PDF..." -ForegroundColor Cyan

python analysis/generate_pdf.py results/ --presentation presentation.md