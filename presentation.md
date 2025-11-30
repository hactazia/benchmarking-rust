# Analyse Comparative des Algorithmes de Recherche

## Introduction

### Objectif du Projet

Comparer les performances de **5 algorithmes de recherche** sur des problèmes classiques d'intelligence artificielle.

### Algorithmes Étudiés

| Algorithme | Type | Optimalité | Mémoire |
|------------|------|------------|---------|
| **BFS** (Breadth-First Search) | Non informé | Optimal | O(b^d) |
| **DFS** (Depth-First Search) | Non informé | Non optimal | O(d) |
| **ID** (Iterative Deepening) | Non informé | Optimal | O(d) |
| **A\*** | Informé (heuristique) | Optimal* | O(b^d) |
| **IDA\*** | Informé (heuristique) | Optimal* | O(d) |

- **BFS** (Breadth-First Search): Le BFS explore tous les nœuds au niveau actuel avant de passer au suivant.
- **DFS** (Depth-First Search): Le DFS explore toutes les feuilles d'une branche avant de revenir en arrière.
- **ID** (Iterative Deepening): Combine les avantages de BFS et DFS en effectuant des recherches DFS avec des profondeurs croissantes.
- **A\*** (A-Star): Un algorithme informé utilisant une heuristique pour guider la recherche.
- **IDA\*** (Iterative Deepening A-Star): Variante d'A* utilisant une approche de profondeur itérative.

*\*Avec une heuristique admissible (ei. ne surestime jamais le coût)*  
*d = profondeur de la solution (ie. nombre de coups)*  
*b = facteur de branchement (ie. nombre moyen de successeurs)*  
*Informé = utilise une heuristique pour guider la recherche*  

### Problèmes Testés

1. **Taquin** : 3×3 et 4×4
2. **Plus Court Chemin** : Grilles 10×10, 100×100, 1000×1000
3. **Graphes Aléatoires** : 50, 200, 500 nœuds

---

## Implémentation

### Choix Technologiques

- **Rust** pour le moteur de benchmarking : performances, sécurité mémoire
- **Python** pour l'analyse : pandas, matplotlib pour les visualisations
- **Heuristique Manhattan** pour A\* et IDA\* sur le Taquin

---

## Résultats Expérimentaux

### Taquin 3×3 (20 instances)

| Algorithme | Temps | Mémoire | Nœuds Visités | Longueur Solution | Succès |
|------------|-------|---------|---------------|-------------------|--------|
| **A\*-Manhattan** | **6.50 ms** | 25 Ko | **680** | 19.4 | 20/20 |
| IDA\*-Manhattan | 7.70 ms | **0 Ko** | 1227 | 18.1 | 20/20 |
| ID | 663.45 ms | 332 Ko | 184507 | 21.2 | 20/20 |
| DFS | 1374.21 ms | 1415 Ko | 92668 | 87.8 | 19/20 |
| BFS | 3068.30 ms | 823 Ko | 26856 | 16.1 | 20/20 |

**Observation clé** : A\* est **~470× plus rapide** que BFS grâce à l'heuristique Manhattan.

### Taquin 4×4 (5 instances)

| Algorithme | Temps | Mémoire | Nœuds Visités | Succès |
|------------|-------|---------|---------------|--------|
| **A\*-Manhattan** | **743 ms** | 3179 Ko | 70634 | 5/5 |
| IDA\*-Manhattan | 2344 ms | **0 Ko** | 890860 | 4/5 |
| BFS | Timeout | — | 79104 | 0/5 |
| DFS | Timeout | — | 3342733 | 0/5 |
| ID | Timeout | 36445 Ko | 18331256 | 0/5 |

**Observation clé** : Seuls A\* et IDA\* réussissent sur le Taquin 4×4. A\* est plus rapide mais consomme plus de mémoire.

### Plus Court Chemin - Grilles

| Taille | Meilleur Algo | Temps | Mémoire | Nœuds Visités |
|--------|---------------|-------|---------|---------------|
| 10×10 | IDA\* | 0 ms | 0 Ko | 19 |
| 100×100 | IDA\* | 3.30 ms | 0 Ko | 199 |
| 1000×1000 | **IDA\*** | **320.60 ms** | **0 Ko** | 1999 |

**Observation clé** : IDA\* excelle sur les grilles avec un comportement linéaire optimal. BFS et ID timeout sur 1000×1000.

### Plus Court Chemin - Graphes Aléatoires

| Taille | Meilleur Algo | Temps | Mémoire | Nœuds Visités | Succès |
|--------|---------------|-------|---------|---------------|--------|
| 50 nœuds | A\* | 0 ms | 0 Ko | 16 | 10/10 |
| 200 nœuds | A\* | 0 ms | 0 Ko | 56 | 10/10 |
| 500 nœuds | BFS | 0.25 ms | 2 Ko | 238 | 4/5 |

**Observation clé** : Sur les graphes aléatoires, A\* et BFS sont très efficaces. Les échecs (1/5 sur 500 nœuds) sont dus à des graphes non connexes.

---

## Analyse Comparative

### Forces et Faiblesses

| Algorithme | Forces | Faiblesses |
|------------|--------|------------|
| **BFS** | Optimal, complet | Explosion mémoire O(b^d) |
| **DFS** | Mémoire minimale O(d) | Non optimal, peut se perdre |
| **ID** | Optimal + mémoire O(d) | Revisite beaucoup de nœuds |
| **A\*** | Très rapide avec bonne heuristique | Mémoire importante |
| **IDA\*** | Optimal + mémoire O(d) + rapide | Revisites (moins que ID) |

### Impact de l'Heuristique

L'heuristique Manhattan réduit drastiquement les nœuds explorés :

- **Sans heuristique (BFS)** : 26856 nœuds sur Taquin 3×3
- **Avec Manhattan (A\*)** : 680 nœuds → **~40× moins**

### Trade-offs Observés

| Trade-off | Explication |
|-----------|-------------|
| **Temps ↔ Mémoire** | A\* rapide mais gourmand (3179 Ko sur Taquin 4×4), IDA\* 0 Ko |
| **Optimalité ↔ Performance** | DFS solutions 5× plus longues (87.8 vs 16.1 coups) |

---

## Explications des Résultats

### Pourquoi A\* est-il si rapide ?

A\* utilise f(n) = g(n) + h(n) :

- **g(n)** : coût réel depuis le départ → garantit l'optimalité
- **h(n)** : estimation heuristique → guide vers la solution

### Pourquoi IDA\* consomme 0 Ko ?

- Recherche en profondeur avec seuil croissant
- Ne stocke que le chemin courant (pas de frontière)
- Compromis : recalcul des nœuds à chaque itération

### Pourquoi BFS échoue sur les grands problèmes ?

- Doit stocker toute la frontière : O(b^d) nœuds
- Taquin 4×4 : ~10^13 états possibles
- La mémoire devient le facteur limitant

---

## Recommandations

| Contrainte | Algorithme | Justification |
|------------|------------|---------------|
| Mémoire limitée | **IDA\*** | 0 Ko constant sur toutes les instances |
| Temps critique + heuristique disponible | **A\*** | 6.50 ms sur Taquin-3×3, 743 ms sur Taquin-4×4 |
| Grandes grilles régulières | **IDA\*** | 320 ms sur 1000×1000 avec 0 Ko (seul à réussir) |
| Graphes aléatoires | **A\*** | 0 ms sur 50-200 nœuds, 100% succès |
| Petite grille sans heuristique | BFS | 93 ms sur 100×100, garanti optimal |
| Exploration rapide (non optimal) | DFS | Solutions trouvées rapidement mais 5× plus longues |

---

## Conclusion

### Résultats Clés

1. **A\*** est le plus rapide avec une bonne heuristique (743 ms sur Taquin-4×4)
2. **IDA\*** est le meilleur choix mémoire : 0 Ko constant, optimal, performant
3. **BFS** limité aux petites instances (timeout sur 1000×1000 et Taquin-4×4)
4. **DFS** rapide mais solutions non optimales (5× plus longues)
5. L'**heuristique Manhattan** fait la différence (~40× moins de nœuds)

### Difficultés Rencontrées

- Gestion de l'explosion combinatoire sur Taquin 4×4
- Équilibrage des paramètres de benchmark
- Génération d'instances représentatives

### Perspectives

- Tester d'autres heuristiques (Pattern Databases)
- Parallélisation des algorithmes
- Extension à d'autres problèmes (CSP, jeux)
