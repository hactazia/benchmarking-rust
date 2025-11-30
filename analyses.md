# Analyse des Résultats

## Synthèse Générale

Ce rapport présente l'analyse comparative de cinq algorithmes de recherche :

- **BFS** (Breadth-First Search)
- **DFS** (Depth-First Search)
- **ID** (Iterative Deepening)
- **A\*** (A-Star)
- **IDA\*** (Iterative Deepening A*).

## Tendances Générales

### Performance Temporelle

- **A\*** et **IDA\*** sont généralement les plus rapides grâce à leur heuristique qui guide la recherche vers la solution.
- **BFS** garantit l'optimalité mais explore de nombreux nœuds inutiles.
- **DFS** peut être rapide mais ne garantit pas la solution optimale.
- **ID** combine les avantages de BFS (optimalité) avec une meilleure gestion mémoire.

### Consommation Mémoire

- **DFS** et **IDA\*** ont une consommation mémoire linéaire O(d) où d est la profondeur.
- **BFS** et **A\*** ont une consommation exponentielle O(b^d) où b est le facteur de branchement.
- **ID** a une consommation mémoire similaire à DFS malgré les recalculs.

### Nœuds Explorés

- Les algorithmes informés (A*, IDA*) explorent significativement moins de nœuds.
- BFS explore tous les nœuds à chaque niveau avant de passer au suivant.
- DFS peut explorer des branches profondes inutilement.

## Analyse par Problème

### Taquin

Le taquin est un problème classique avec un espace d'états bien défini :

- **A\*-Manhattan** est le plus rapide sur le 3×3 (0.25ms) avec seulement 213 nœuds visités.
- **IDA\*-Manhattan** excelle sur le 4×4 (644ms vs 4487ms pour A*) avec 0 Ko de mémoire.
- **BFS** est 32000× plus lent que A* sur le 3×3 (8012ms) et échoue sur le 4×4.
- **DFS** trouve des solutions mais très longues (46 coups vs 16 pour A*) et visite 500× plus de nœuds.
- **ID** garantit l'optimalité mais revisite énormément de nœuds (346024 vs 213 pour A*).

### Plus Court Chemin

Pour la recherche de chemin dans les graphes :

- **IDA\*** domine sur les grandes grilles (1000×1000) avec 0 Ko de mémoire et des temps excellents (247ms).
- **A\*** est performant mais consomme beaucoup de mémoire sur les grandes instances (559 Ko).
- **BFS** échoue sur les très grandes grilles (timeout sur 1000×1000) à cause de l'explosion mémoire.
- **DFS** trouve des solutions mais elles sont très longues (non optimales).
- Sur les graphes aléatoires, **A\*** et **IDA\*** ont des performances similaires.

## Explications des Résultats

### Pourquoi A* est-il souvent le meilleur ?

A* utilise une fonction d'évaluation f(n) = g(n) + h(n) qui :
1. **g(n)** : coût réel depuis le départ (garantit l'optimalité)
2. **h(n)** : estimation du coût restant (guide vers la solution)

Cette combinaison permet d'explorer prioritairement les chemins les plus prometteurs.

### Pourquoi IDA* consomme-t-il moins de mémoire ?

IDA* effectue des recherches en profondeur itératives avec un seuil croissant :
- Chaque itération ne stocke que le chemin courant (linéaire en profondeur)
- Le seuil augmente progressivement jusqu'à trouver la solution
- Compromis : recalcul des nœuds mais économie de mémoire significative

### Pourquoi BFS échoue-t-il sur les grands problèmes ?

BFS doit stocker tous les nœuds de la frontière :
- Pour un facteur de branchement b et une profondeur d : O(b^d) nœuds
- Taquin 4×4 : environ 10^13 états possibles
- La mémoire devient le facteur limitant avant le temps

### Pourquoi DFS ne trouve-t-il pas toujours de solution ?

DFS explore en profondeur sans limite :
- Peut s'enfoncer dans des branches infinies ou très profondes
- Ne garantit pas l'optimalité même quand il trouve une solution
- Sensible à l'ordre d'exploration des successeurs

## Recommandations

| Situation | Algorithme Recommandé | Justification (données) |
|-----------|----------------------|------------------------|
| Solution optimale + mémoire limitée | IDA* | 0 Ko sur toutes les instances |
| Solution optimale + temps critique | A* | 0.25ms sur Taquin-3x3 |
| Grandes grilles | IDA* | 247ms sur 1000×1000 vs timeout BFS |
| Graphe simple petit | BFS | Fonctionne bien sur 10×10 et graphes aléatoires |
| Exploration rapide sans optimalité | DFS | Rapide mais solutions 3× plus longues |

## Conclusion

Les résultats confirment les tendances théoriques :

- **IDA\*** est le meilleur choix global : 0 Ko de mémoire, solutions optimales, et performances excellentes même sur les grandes instances (1000×1000).
- **A\*** est le plus rapide quand la mémoire n'est pas une contrainte, mais peut consommer beaucoup (6202 Ko sur Taquin-4×4).
- **BFS** est limité aux petites instances à cause de sa consommation mémoire exponentielle.
- **DFS** est rapide mais produit des solutions 2-3× plus longues que l'optimal.
- **ID** offre un bon compromis mais revisite beaucoup de nœuds (346024 vs 213 pour A* sur Taquin).
