# Références et Ressources

## Algorithmes de Recherche

### Livres
- **Artificial Intelligence: A Modern Approach** (Russell & Norvig)
  - Chapitres 3 et 4 : Recherche non-informée et informée
  - Référence standard pour les algorithmes de recherche

- **Introduction to Algorithms** (CLRS)
  - Chapitre 22 : Graphes et parcours
  - Analyse de complexité

### Articles Académiques

- **A Formal Basis for the Heuristic Determination of Minimum Cost Paths**
  - Peter Hart, Nils Nilsson, Bertram Raphael (1968)
  - Article original de A*

- **Depth-First Iterative-Deepening: An Optimal Admissible Tree Search**
  - Richard Korf (1985)
  - Introduction d'IDDFS et IDA*

## Problèmes Types

### Taquin (Sliding Puzzle)

- **Finding Optimal Solutions to the Twenty-Four Puzzle**
  - Richard Korf (1996)
  - Techniques pour résoudre le 24-puzzle

- **The N-puzzle problem**
  - Complexité : NP-complet pour N ≥ 3
  - Base de données de patterns

### Heuristiques

- **Distance de Manhattan** : h(n) = Σ |x_goal - x_current| + |y_goal - y_current|
  - Admissible pour le Taquin
  - Facile à calculer

- **Distance de Hamming** : h(n) = nombre de tuiles mal placées
  - Également admissible mais moins informative

- **Linear Conflict** : Amélioration de Manhattan
  - Prend en compte les conflits sur les lignes/colonnes

## Optimisations Implémentées

### Parallélisation avec Rayon
- **Work-stealing thread pool** : Distribution dynamique des tâches
- **Exécution simultanée** : Tous algorithmes × toutes instances en parallèle
- **Auto-détection CPU** : Utilisation optimale des cœurs disponibles
- **Documentation** : https://docs.rs/rayon/

### Timeout Mechanism
- **std::sync::mpsc channels** : Communication inter-threads
- **recv_timeout()** : Limite de temps configurable par algorithme
- **Enregistrement des erreurs** : Timeouts sauvegardés dans le JSON

### Reproductibilité
- **Seeds pour graphes aléatoires** : Basées sur timestamp nanoseconde
- **StdRng avec SeedableRng** : Générateur déterministe
- **Traçabilité** : Seeds enregistrées dans les résultats

### Architecture Générique
- **Traits Rust** : `Problem`, `SearchAlgorithm`
- **Code refactorisé** : Helpers génériques réutilisables
- **Réduction de duplication** : ~81% de code en moins dans runner.rs

## Outils et Technologies

### Rust
- **Documentation officielle** : https://doc.rust-lang.org/
- **The Rust Book** : https://doc.rust-lang.org/book/
- **Rust by Example** : https://doc.rust-lang.org/rust-by-example/

### Python pour l'Analyse
- **Pandas** : https://pandas.pydata.org/
- **Matplotlib** : https://matplotlib.org/
- **Seaborn** : https://seaborn.pydata.org/

## Benchmarking

### Métriques de Performance

1. **Temps d'exécution**
   - Wall-clock time
   - Permet de comparer les performances réelles

2. **Mémoire**
   - Peak memory usage
   - Crucial pour les grands espaces de recherche

3. **Nœuds explorés**
   - Mesure directe de l'efficacité de l'algorithme
   - Indépendant du matériel

4. **Facteur de branchement effectif (EBF)**
   - Mesure de l'efficacité de l'heuristique
   - b* tel que N = 1 + b* + (b*)² + ... + (b*)^d
   - Où N = nombre total de nœuds, d = profondeur de la solution

## Complexité Algorithmique

### Notation Big-O

- **BFS** : O(b^d) en temps et espace
  - b = facteur de branchement
  - d = profondeur de la solution

- **DFS** : O(b^m) en temps, O(bm) en espace
  - m = profondeur maximale

- **Iterative Deepening** : O(b^d) en temps, O(bd) en espace
  - Combine avantages de BFS et DFS

- **A*** : O(b^d) dans le pire cas
  - Performance dépend de l'heuristique
  - Optimal si h(n) est admissible

- **IDA*** : O(b^d) en temps, O(d) en espace
  - Meilleure utilisation de la mémoire que A*

## Propriétés des Algorithmes

| Algorithme | Complet | Optimal | Temps | Espace |
|------------|---------|---------|-------|--------|
| BFS | Oui | Oui* | O(b^d) | O(b^d) |
| DFS | Non** | Non | O(b^m) | O(bm) |
| ID | Oui | Oui* | O(b^d) | O(bd) |
| A* | Oui*** | Oui**** | O(b^d) | O(b^d) |
| IDA* | Oui*** | Oui**** | O(b^d) | O(d) |

\* Si tous les coûts sont égaux  
\*\* Dans les graphes infinis  
\*\*\* Si l'espace est fini  
\*\*\*\* Si l'heuristique est admissible

## Ressources en Ligne

- **VisuAlgo** : https://visualgo.net/
  - Visualisations d'algorithmes

- **GitHub** : Repositories de référence
  - Implémentations en différents langages
  - Comparaisons de performances

- **Stack Exchange - Computer Science**
  - Discussions sur les algorithmes de recherche
  - Clarifications théoriques

## Pour Aller Plus Loin

### Optimisations Possibles

1. **Pattern Databases**
   - Précalcul d'heuristiques
   - Améliore drastiquement A*/IDA*

2. **Bidirectional Search**
   - Recherche depuis début et fin simultanément
   - Réduit l'espace de recherche

3. **Jump Point Search**
   - Optimisation pour grilles uniformes
   - Évite les nœuds redondants

4. **Fringe Search**
   - Alternative à A* avec meilleure cache locality

### Variantes du Taquin

- **Manhattan avec Linear Conflict**
- **Disjoint Pattern Databases**
- **Walking Distance heuristic**

## Citation de ce Projet

```bibtex
@misc{benchmarking-rust-2025,
  title={Benchmarking d'Algorithmes de Recherche},
  author={[Vos Noms]},
  year={2025},
  note={Projet académique - Comparaison BFS, DFS, ID, A*, IDA*}
}
```
