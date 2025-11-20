# Guide d'Utilisation

## Installation

### 1. Installer Rust

```powershell
# Télécharger et installer rustup
winget install Rustlang.Rustup
# Ou via https://rustup.rs/
```

### 2. Installer Python et dépendances

```powershell
# Installer Python 3.8+
winget install Python.Python.3.11

# Installer les dépendances Python
pip install -r requirements.txt
```

## Compilation du Projet

```powershell
# Mode debug
cargo build

# Mode release (optimisé pour les performances)
cargo build --release
```

## Exécution des Benchmarks

### Benchmark Complet

```powershell
# Tous les algorithmes sur le Taquin 3x3, 10 itérations
cargo run --release

# Résultats sauvegardés dans: results/benchmark_results.json
```

### Benchmarks Spécifiques

```powershell
# Taquin 3x3 uniquement avec A*
cargo run --release -- --algorithm astar --problem taquin --size 3 --iterations 5

# Taquin 4x4 avec tous les algorithmes
cargo run --release -- --problem taquin --size 4 --iterations 5

# Plus court chemin
cargo run --release -- --problem shortest-path --size 10 --iterations 10

# BFS uniquement sur tous les problèmes
cargo run --release -- --algorithm bfs --iterations 10
```

### Options Disponibles

- `--algorithm` ou `-a`: Algorithme à tester
  - `all` (défaut) : Tous les algorithmes
  - `bfs` : Breadth-First Search
  - `dfs` : Depth-First Search
  - `id` : Iterative Deepening
  - `astar` : A*
  - `idastar` : IDA*

- `--problem` ou `-p`: Problème à résoudre
  - `all` (défaut) : Tous les problèmes
  - `taquin` : Problème du Taquin
  - `shortest-path` : Plus court chemin

- `--size` ou `-s`: Taille du problème
  - Pour Taquin: 3, 4, ou 5 (défaut: 3)
  - Pour shortest-path: taille de la grille

- `--iterations` ou `-i`: Nombre d'instances à tester (défaut: 10)

- `--output` ou `-o`: Fichier de sortie (défaut: results/benchmark_results.json)

- `--threads` ou `-t`: Nombre de threads pour l'exécution parallèle (défaut: 0 = auto-détection CPU)

- `--timeout`: Timeout en secondes pour chaque algorithme (défaut: 60)

### Types de Problèmes

**Taquin (`taquin`):**
- Généré par mouvements aléatoires depuis l'état but
- Garantit la solvabilité
- État initial affiché sous forme de grille

**Plus Court Chemin - Grille (`shortest-path`):**
- Graphe en grille régulière (4 voisins par nœud)
- Heuristique : distance de Manhattan
- Déterministe

**Plus Court Chemin - Graphe Aléatoire (`shortest-path-random`):**
- Graphe généré avec seed basée sur timestamp
- Heuristique aléatoire (sous-estimation)
- Reproductible via la seed enregistrée
- Seed affichée dans les résultats JSON

## Analyse des Résultats

### Génération des Graphiques

```powershell
# Générer tous les graphiques
python analysis/visualize.py

# Graphiques sauvegardés dans: results/plots/
```

### Fusion de Résultats

```powershell
# Fusionner plusieurs fichiers de résultats pour analyse de scalabilité
python analysis/merge_results.py results/shortest_path_all.json results/shortest_path_10.json results/shortest_path_100.json results/shortest_path_1000.json

# Résultat: results/shortest_path_all.json avec toutes les tailles
```

### Traitement par Répertoire

```powershell
# Générer visualisations et rapports pour tous les JSON dans results/
python analysis/visualize.py results/
python analysis/generate_report.py results/

# Structure générée:
# results/visuals/<fichier>/    → Graphiques
# results/reports/<fichier>/    → Rapports (index.md + details.md)
```

### Génération du Rapport

```powershell
# Générer le rapport complet
python analysis/generate_report.py results/file.json

# Rapport sauvegardé dans: docs/rapport.md
```

### Analyse avec un fichier spécifique

```powershell
python analysis/visualize.py results/my_benchmark.json
python analysis/generate_report.py results/my_benchmark.json
```

## Workflow Complet

### Option 1 : Script Automatisé

```powershell
# Windows
.\start.ps1

# Linux/Mac
chmod +x start.sh
./start.sh
```

Le script exécute automatiquement :
1. Compilation en mode release
2. Série de benchmarks (Taquin 3x3/4x4, grilles 10/100/1000, graphes 50/200/500)
3. Fusion des résultats
4. Génération des visualisations
5. Création des rapports

### Option 2 : Workflow Manuel

```powershell
# 1. Compiler le projet
cargo build --release

# 2. Exécuter les benchmarks (exemple: Taquin 3x3)
cargo run --release -- --problem taquin --size 3 --iterations 10

# 3. (Optionnel) Taquin 4x4
cargo run --release -- --problem taquin --size 4 --iterations 5 --output results/taquin_4x4.json

# 4. Générer les visualisations pour tous les fichiers
python analysis/visualize.py results/

# 5. Générer les rapports
python analysis/generate_report.py results/

# 6. Consulter les résultats
# - Graphiques: results/visuals/<fichier>/
# - Rapports: results/reports/<fichier>/index.md et details.md
# - Données brutes: results/*.json
```

## Tests

```powershell
# Exécuter les tests unitaires
cargo test

# Tests avec affichage détaillé
cargo test -- --nocapture
```

## Dépannage

### Problème de compilation

```powershell
# Nettoyer et recompiler
cargo clean
cargo build --release
```

### Problème Python

```powershell
# Réinstaller les dépendances
pip install -r requirements.txt --upgrade

# Vérifier l'installation
python -c "import pandas, matplotlib, seaborn; print('OK')"
```

### Mémoire insuffisante

Si vous rencontrez des problèmes de mémoire avec les grandes instances:
- Réduire `--iterations`
- Utiliser des tailles plus petites
- Tester un seul algorithme à la fois
- Privilégier IDA* pour les grandes instances

### Algorithmes trop lents

Si les benchmarks prennent trop de temps :
- Utiliser `--timeout` pour limiter le temps par algorithme (ex: `--timeout 30`)
- Réduire le nombre de threads avec `--threads` si la machine surchauffe
- Les timeouts sont enregistrés dans le JSON avec un message d'erreur

### Reproductibilité des graphes aléatoires

Pour reproduire exactement un graphe aléatoire :
1. Consulter la seed dans le fichier JSON : `"initial_state": "Seed: 1763620284822937800"`
2. La seed est générée automatiquement à partir du timestamp en nanosecondes
3. Le graphe est déterministe pour une seed donnée

## Conseils pour la Présentation

1. **Préparer plusieurs configurations:**
   ```powershell
   # Taquin 3x3 - rapide
   cargo run --release -- -p taquin -s 3 -i 20 -o results/taquin_3x3.json
   
   # Taquin 4x4 - plus long
   cargo run --release -- -p taquin -s 4 -i 5 -o results/taquin_4x4.json
   ```

2. **Générer plusieurs rapports:**
   ```powershell
   python analysis/generate_report.py results/taquin_3x3.json
   python analysis/generate_report.py results/taquin_4x4.json
   ```

3. **Comparer les algorithmes:**
   - Regarder les graphiques dans `results/visuals/<fichier>/`
   - Analyser les tendances dans `results/reports/<fichier>/index.md`
   - Consulter les détails des instances dans `details.md`
   - Noter les observations pour la présentation orale

## CI/CD avec GitHub Actions

Le projet inclut un workflow GitHub Actions (`.github/workflows/build-and-benchmark.yml`) qui :

1. **Build multi-plateforme** : Compile le projet pour Windows x64 et Linux x64
2. **Exécution des benchmarks** : Lance automatiquement les tests
3. **Génération des rapports** : Crée visualisations et rapports
4. **Packaging** : Crée des archives ZIP avec binaires + résultats
5. **Release automatique** : Publie les artefacts sur GitHub

Déclenché automatiquement lors des push sur `main`/`master` ou manuellement via l'interface GitHub Actions.
