#!/usr/bin/env python3
"""
Script pour fusionner plusieurs fichiers de résultats JSON en un seul.
Utile pour créer des graphiques de scalabilité avec différentes tailles.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any


def load_json(file_path: str) -> List[Dict[str, Any]]:
    """Charge un fichier JSON de résultats."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print(f"Warning: {file_path} ne contient pas une liste")
                return []
    except FileNotFoundError:
        print(f"Error: {file_path} non trouvé")
        return []
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON dans {file_path}: {e}")
        return []


def merge_results(input_files: List[str], output_file: str) -> None:
    """Fusionne plusieurs fichiers JSON en un seul."""
    print("Fusion de Résultats JSON")
    
    all_results = []
    
    # Charger tous les fichiers
    for file_path in input_files:
        print(f"Chargement de {file_path}...")
        results = load_json(file_path)
        if results:
            all_results.extend(results)
            print(f"   {len(results)} résultats chargés")
        else:
            print(f"   Aucun résultat chargé")
    
    if not all_results:
        print("\nAucun résultat à fusionner!")
        sys.exit(1)
    
    # Sauvegarder le fichier fusionné
    print(f"\nSauvegarde dans: {output_file}")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # Afficher les statistiques
    print(f"\nFusion sauvegardée")
    print(f"Total: {len(all_results)} résultats")
    
    # Grouper par problème et taille
    problems = {}
    for result in all_results:
        problem = result.get('problem', 'Unknown')
        size = result.get('problem_size', 0)
        key = f"{problem} (taille {size})"
        problems[key] = problems.get(key, 0) + 1
    
    print("\nRésumé par problème:")
    for problem, count in sorted(problems.items()):
        print(f"   - {problem}: {count} résultats")


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 3:
        print("Usage: python merge_results.py <output.json> <input1.json> <input2.json> ...")
        print("\nExemple:")
        print("  python merge_results.py results/shortest_path_all.json \\")
        print("         results/shortest_path_10.json \\")
        print("         results/shortest_path_100.json \\")
        print("         results/shortest_path_1000.json")
        sys.exit(1)
    
    output_file = sys.argv[1]
    input_files = sys.argv[2:]
    
    # Vérifier que les fichiers d'entrée existent
    missing_files = [f for f in input_files if not Path(f).exists()]
    if missing_files:
        print("Fichiers manquants:")
        for f in missing_files:
            print(f"   - {f}")
        sys.exit(1)
    
    merge_results(input_files, output_file)


if __name__ == "__main__":
    main()
