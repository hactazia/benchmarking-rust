# Benchmarking d'Algorithmes de Recherche

Projet d'évaluation et comparaison des performances d'algorithmes de recherche (BFS, DFS, ID, A*, IDA*) sur différents problèmes types.

## 🎯 Objectifs

- Implémenter plusieurs algorithmes de recherche en Rust
- Tester sur différents problèmes (Taquin, plus court chemin, etc.)
- Analyser les performances (temps, mémoire, nœuds visités)
- Visualiser et comparer les résultats avec Python

## 📊 Algorithmes Implémentés

- **BFS** (Breadth-First Search)
- **DFS** (Depth-First Search)
- **ID** (Iterative Deepening)
- **A\*** (A-Star)
- **IDA\*** (Iterative Deepening A-Star)

## 🧩 Problèmes Types

1. **Taquin** (Sliding Puzzle)
   - Tailles: 3x3, 4x4
   - Multiples initialisations
   - Heuristiques: Manhattan, Hamming
   - État initial capturé dans les résultats JSON

2. **Plus Court Chemin** (Shortest Path)
   - Graphes de différentes tailles (10x10, 100x100, 1000x1000)
   - Tests de scalabilité
   - Tous les algorithmes supportés (BFS, DFS, ID, A*, IDA*)

## 🚀 Installation et Utilisation

### Prérequis

- Rust 1.70+ (`rustup install stable`)
- Python 3.8+ avec pip

### Installation

#### Option 1 : Télécharger les binaires pré-compilés

Téléchargez les exécutables et résultats depuis les [Releases GitHub](https://github.com/hactazia/benchmarking-rust/releases) :
- `benchmarking-rust-windows-x64.zip` - Windows 64-bit
- `benchmarking-rust-linux-x64.zip` - Linux 64-bit

Chaque archive contient :
- L'exécutable compilé (`results/bin/`)
- Les résultats JSON des benchmarks
- Tous les graphiques et rapports générés

#### Option 2 : Compiler depuis les sources

```bash
# Compiler le projet Rust
cargo build --release

# Installer les dépendances Python
pip install -r requirements.txt
```

### Exécution des Benchmarks

```bash
# Exécuter tous les benchmarks
cargo run --release

# Exécuter un problème spécifique
cargo run --release -- --problem taquin --size 3

# Exécuter avec un algorithme spécifique
cargo run --release -- --algorithm astar --problem taquin

# Contrôler le nombre de threads (0 = auto-détection CPU)
cargo run --release -- --threads 8

# Suite complète avec script PowerShell
.\run_benchmarks.ps1
```

### Analyse des Résultats

```bash
# Fusionner plusieurs fichiers de résultats
python analysis/merge_results.py results/all.json results/file1.json results/file2.json

# Générer les graphiques et analyses
python analysis/visualize.py results/file.json

# Rapport complet
python analysis/generate_report.py results/file.json
```

## 📈 Métriques Mesurées

- **Temps de calcul** (ms)
- **Mémoire utilisée** (Ko/Mo)
- **Nombre de nœuds visités**
- **Nombre de nœuds générés**
- **Longueur de la solution**
- **Facteur de branchement effectif**
- **État initial** du problème (capturé dans JSON)

## 📁 Structure du Projet

```
benchmarking-rust/
├── src/
│   ├── main.rs                 # Point d'entrée
│   ├── algorithms/             # Algorithmes de recherche
│   │   ├── mod.rs
│   │   ├── bfs.rs
│   │   ├── dfs.rs
│   │   ├── iterative_deepening.rs
│   │   ├── astar.rs
│   │   └── idastar.rs
│   ├── problems/               # Problèmes à résoudre
│   │   ├── mod.rs
│   │   ├── taquin.rs
│   │   └── shortest_path.rs
│   ├── benchmarking/           # Infrastructure de benchmark
│   │   ├── mod.rs
│   │   ├── metrics.rs
│   │   └── runner.rs
│   └── utils/                  # Utilitaires
│       ├── mod.rs
│       └── heuristics.rs
├── analysis/                   # Scripts Python d'analyse
│   ├── visualize.py
│   ├── generate_report.py
│   ├── merge_results.py
│   └── utils.py
├── results/                    # Résultats des benchmarks
│   ├── *.json                  # Données brutes
│   ├── visuals/                # Graphiques générés
│   │   └── <name>/             # Dossier par fichier JSON
│   │       ├── time_comparison.png
│   │       ├── memory_comparison.png
│   │       ├── nodes_comparison.png
│   │       └── success_rate.png
│   └── reports/                # Rapports markdown
│       └── <name>/             # Dossier par fichier JSON
│           ├── index.md        # Rapport principal
│           └── details.md      # Détails par instance
├── docs/                       # Documentation
├── README.md                   # Documentation principale
├── start.ps1                   # Script PowerShell pour benchmarks
├── start.sh                    # Script Bash pour benchmarks
├── Cargo.toml                  # Configuration du projet Rust
└── requirements.txt            # Dépendances Python
```

## 🔬 Résultats Générés

Les benchmarks génèrent plusieurs types de fichiers:

### Données JSON (`results/*.json`)
- Temps d'exécution par algorithme et problème
- Utilisation mémoire
- Statistiques sur les nœuds
- Qualité des solutions
- État initial de chaque instance
- Message d'erreur en cas d'échec (timeout, pas de solution)

### Visualisations (`results/visuals/<name>/`)
- Graphiques de comparaison des temps d'exécution
- Utilisation mémoire
- Nœuds explorés
- Taux de succès

### Rapports Markdown (`results/reports/<name>/`)
- **index.md**: Vue d'ensemble, statistiques agrégées, analyses comparatives
- **details.md**: Détails de chaque instance triés par problème, algorithme et succès