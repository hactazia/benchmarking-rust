# Structure du Projet

```
benchmarking-rust/
│
├── Cargo.toml                  # Configuration du projet Rust
├── README.md                   # Documentation principale
├── requirements.txt            # Dépendances Python
├── start.ps1                   # Script de démarrage (Windows)
├── start.sh                    # Script de démarrage (Linux/Mac)
├── run_benchmarks.ps1          # Script de benchmarks complets
│
├── src/                        # Code source Rust
│   ├── main.rs                # Point d'entrée du programme
│   │
│   ├── algorithms/            # Implémentations des algorithmes
│   │   ├── mod.rs            # Module principal + traits
│   │   ├── bfs.rs            # Breadth-First Search
│   │   ├── dfs.rs            # Depth-First Search
│   │   ├── iterative_deepening.rs  # Iterative Deepening
│   │   ├── astar.rs          # A* Search
│   │   └── idastar.rs        # IDA* Search
│   │
│   ├── problems/              # Définitions des problèmes
│   │   ├── mod.rs            # Module principal
│   │   ├── taquin.rs         # Problème du Taquin (Sliding Puzzle)
│   │   └── shortest_path.rs  # Plus court chemin (grille et graphes aléatoires avec seeds)
│   │
│   ├── benchmarking/          # Infrastructure de benchmark
│   │   ├── mod.rs            # Module principal
│   │   ├── metrics.rs        # Définition des métriques
│   │   └── runner.rs         # Exécution des benchmarks
│   │
│   └── utils/                 # Utilitaires
│       ├── mod.rs            # Module principal
│       └── heuristics.rs     # Fonctions heuristiques
│
├── analysis/                   # Scripts Python d'analyse
│   ├── visualize.py          # Génération de graphiques
│   ├── generate_report.py   # Génération du rapport
│   ├── merge_results.py     # Fusion de fichiers JSON
│   └── utils.py              # Fonctions utilitaires
│
├── results/                    # Résultats des benchmarks
│   ├── *.json                 # Données brutes (générés)
│   │
│   ├── visuals/               # Graphiques (générés par visualize.py)
│   │   └── <name>/           # Dossier par fichier JSON
│   │       ├── time_comparison.png
│   │       ├── memory_comparison.png
│   │       ├── nodes_comparison.png
│   │       ├── success_rate.png
│   │       ├── size_scaling.png
│   │       └── heatmap_time.png
│   │
│   └── reports/               # Rapports markdown (générés par generate_report.py)
│       └── <name>/           # Dossier par fichier JSON
│           ├── index.md      # Rapport principal (vue d'ensemble, stats)
│           └── details.md    # Détails de chaque instance
│
├── instances/                  # Instances de test
│   ├── README.md
│   └── taquin_3x3.json       # Instances prédéfinies
│
├── .github/                    # GitHub Actions CI/CD
│   └── workflows/
│       └── build-and-benchmark.yml  # Build multi-plateforme et benchmarks
│
└── docs/                       # Documentation
    ├── guide.md               # Guide d'utilisation
    ├── structure.md           # Ce fichier
    ├── references.md          # Références
    └── checklist_presentation.md  # Checklist pour la présentation
```

## Description des Modules

### `src/algorithms/`

Contient les implémentations de tous les algorithmes de recherche. Chaque algorithme implémente le trait `SearchAlgorithm` défini dans `mod.rs`.

**Trait principal:**
```rust
pub trait SearchAlgorithm {
    fn search<P: Problem>(&self, problem: &P) -> SearchResult;
    fn name(&self) -> &str;
}
```

### `src/problems/`

Définit les problèmes sur lesquels les algorithmes sont testés. Chaque problème implémente le trait `Problem`.

**Trait principal:**
```rust
pub trait Problem {
    type State: Clone + Eq + Hash;
    fn initial_state(&self) -> Self::State;
    fn is_goal(&self, state: &Self::State) -> bool;
    fn successors(&self, state: &Self::State) -> Vec<(Self::State, usize)>;
    fn heuristic(&self, state: &Self::State) -> usize;
}
```

### `src/benchmarking/`

Infrastructure pour exécuter les benchmarks et collecter les métriques:
- **Temps d'exécution** (ms)
- **Mémoire utilisée** (Ko)
- **Nœuds visités**
- **Nœuds générés**
- **Longueur de la solution**
- **Facteur de branchement effectif**
- **État initial** du problème (grilles formatées, seeds pour graphes aléatoires)
- **Messages d'erreur** (timeout, pas de solution)
- **Exécution parallèle optimisée** : Tous les algorithmes × toutes les instances s'exécutent simultanément avec Rayon
- **Timeout configurable** (défaut 60s) pour éviter les exécutions infinies
- **Code générique refactorisé** : helpers réutilisables pour tous types de problèmes

### `analysis/`

Scripts Python pour l'analyse post-benchmark:
- Chargement des données JSON
- Calcul de statistiques
- Génération de graphiques comparatifs
- Création de rapports automatiques

**Organisation des résultats générés:**

```
results/
├── fichier.json                        # Données brutes
├── visuals/fichier/                    # Graphiques
│   ├── time_comparison.png
│   ├── memory_comparison.png
│   ├── nodes_comparison.png
│   ├── success_rate.png
│   ├── size_scaling.png
│   └── heatmap_time.png
└── reports/fichier/                    # Rapports
    ├── index.md                        # Rapport principal
    └── details.md                      # Détails par instance
```

**Structure du rapport `index.md`:**
- Vue d'ensemble (nombre de tests, taux de succès)
- Statistiques résumées par algorithme
- Analyse comparative (meilleur temps, mémoire, nœuds)
- Visualisations (liens vers les graphiques)

**Structure du rapport `details.md`:**
- Trié par : Problème → Algorithme → Succès (✅ puis ❌)
- Taux de succès par algorithme
- Pour chaque instance :
  - Métriques complètes (si succès)
  - Message d'erreur (si échec : timeout, pas de solution)
  - État initial du problème (dans un bloc déroulant)

## Flux de Données

1. **Exécution** (`src/main.rs`)
   - Parse les arguments CLI
   - Configure le benchmark
   - Lance `BenchmarkRunner`

2. **Benchmark** (`src/benchmarking/runner.rs`)
   - Génère les instances
   - Exécute chaque algorithme
   - Collecte les métriques
   - Sauvegarde en JSON

3. **Analyse** (`analysis/`)
   - Charge les résultats JSON
   - Calcule les statistiques
   - Génère les visualisations
   - Produit le rapport

## Extension du Projet

### Ajouter un Nouvel Algorithme

1. Créer `src/algorithms/mon_algo.rs`
2. Implémenter le trait `SearchAlgorithm`
3. Ajouter dans `src/algorithms/mod.rs`:
   ```rust
   pub mod mon_algo;
   ```
4. Ajouter dans `runner.rs` pour l'inclure aux benchmarks

### Ajouter un Nouveau Problème

1. Créer `src/problems/mon_probleme.rs`
2. Implémenter le trait `Problem`
3. Ajouter dans `src/problems/mod.rs`
4. Ajouter la logique dans `runner.rs`

### Ajouter une Nouvelle Métrique

1. Ajouter le champ dans `struct Metrics` (`metrics.rs`)
2. Mettre à jour les algorithmes pour collecter la métrique
3. Mettre à jour les scripts Python pour la visualiser
