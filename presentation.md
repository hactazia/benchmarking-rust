# Présentation du projet

Le projet est disponible sur [GitHub](https://github.com/hactazia/benchmarking-rust) avec les resultats des benchmarks posté dans les [Releases](https://github.com/hactazia/benchmarking-rust/releases/latest).  
Vous pourrez y trouver les codes sources des IA benchmarkées,  
les executables, ainsi que les résultats des tests effectués et le pdf récapitulatif.  
Les resultats peuvent être différents sur les releases que sur votre machine locale, 
 car les performances des Github Actions peuvent varier.  
La première partie du rapport pdf fait l'analyse des résultats obténus sur des resultats locaux,  
tandis que la seconde partie qui est généré automatiquement à partir des résultats du Github Actions.

J'ai choisi de benchmarker avec le Rust car c'est un language que je trouve pertinent pour les performances, la gestion mémoire, et du multi-threading.  
Pour la partie avalyse, j'ai utilisé du python par la simplicité pour la generation des graphiques et la création du rapport.

Les IA benchmarkées sont :
- BFS
- DFS
- A*
- ID
- IDA*

Et certains avec des heuristiques différentes (Hamming et Manhattan pour A* et IDA*).

Je les ai benchmarkées sur differents types de problèmes comme :
- Taquin
- Chemin dans une grille

Pour le taquin, j'ai fait plusieurs tailles (3x3, 4x4) généré aleatoirement à partir d'une seed mit en complement dans les instances.  
Pour la grille, j'ai fait des grilles de différentes tailles (10x10, 100x100 et 1000x1000) avec des generations simple et une seconde partie en generation aléatoire.

Le recapitulatif de toutes les instances est disponible dans `all`.

## Résumé des résultats

(Voir le rapport pdf partie taquin)

Pour le taquin 3x3 et 4x4, IDA* avec l'heuristique Manhattan est l'IA la plus performante en temps et en mémoire. Et A* Manhattan est aussi très performant sur le la visite du moins de noeuds.
On peut aussi noter que BFS et DFS sont très mauvais sur ce type de problème.  
Cela peut s'expliquer par le fait que le taquin a un grand facteur de branchement et une profondeur importante, ce qui pénalise fortement les algorithmes non informés.

(Voir le rapport pdf partie shortest path)

Pour les grilles, genérées de manière simple, BFS est l'IA la plus performante en temps, mais IDA* se montre bien plus performant dans tous les autres domaines quand la taille de la grille augmente.

(Voir le rapport pdf partie shortest path random)

Pour les grilles générées aléatoirement, A* est largement l'IA la plus performante pour toutes tailes confondues, que ce soit en temps, en mémoire ou en nombre de noeuds visités.

## Conclusion

En conclusion, les algorithmes informés (A* et IDA*) sont globalement plus performants que les algorithmes non informés (BFS, DFS, ID) sur les problèmes testés, en particulier lorsque des heuristiques efficaces sont utilisées.