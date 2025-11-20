"""
Script de génération de rapport
Crée un rapport complet avec statistiques et analyses
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from tabulate import tabulate


class ReportGenerator:
    def __init__(self, results_file='results/benchmark_results.json'):
        self.results_file = results_file
        self.df = None
        self.results_raw = None
        # Extraire le nom de base du fichier (sans extension) et le dossier parent
        results_path = Path(results_file)
        self.base_name = results_path.stem
        self.report_dir = results_path.parent / 'reports' / self.base_name
        self.output_file = self.report_dir / 'index.md'
        self.details_file = self.report_dir / 'details.md'
        self.visuals_dir = results_path.parent / 'visuals' / self.base_name
        self.load_data()
    
    def load_data(self):
        """Charge les résultats depuis le fichier JSON"""
        with open(self.results_file, 'r') as f:
            results = json.load(f)
        
        # Conserver les données brutes pour le rapport détaillé
        self.results_raw = results
        
        data = []
        for result in results:
            row = {
                'algorithm': result['algorithm'],
                'problem': result['problem'],
                'problem_size': result['problem_size'],
                'instance_id': result['instance_id'],
                'success': result['success'],
                'time_ms': result['metrics']['time_ms'],
                'memory_kb': result['metrics']['memory_kb'],
                'nodes_visited': result['metrics']['nodes_visited'],
                'nodes_generated': result['metrics']['nodes_generated'],
                'solution_length': result['metrics']['solution_length'],
                'error': result.get('error', None),
            }
            data.append(row)
        
        self.df = pd.DataFrame(data)
    
    def generate_summary_statistics(self):
        """Génère les statistiques résumées"""
        df_success = self.df[self.df['success']]
        
        summary = []
        for (algo, problem), group in df_success.groupby(['algorithm', 'problem']):
            stats = {
                'Algorithme': algo,
                'Problème': problem,
                'Succès': f"{len(group)}/{len(self.df[(self.df['algorithm'] == algo) & (self.df['problem'] == problem)])}",
                'Temps (ms)': f"{group['time_ms'].mean():.2f} ± {group['time_ms'].std():.2f}",
                'Mémoire (Ko)': f"{group['memory_kb'].mean():.0f}",
                'Nœuds Visités': f"{group['nodes_visited'].mean():.0f}",
                'Nœuds Générés': f"{group['nodes_generated'].mean():.0f}",
                'Longueur Sol.': f"{group['solution_length'].mean():.1f}",
            }
            summary.append(stats)
        
        return pd.DataFrame(summary)
    
    def analyze_algorithm_strengths(self):
        """Analyse les points forts de chaque algorithme"""
        df_success = self.df[self.df['success']]
        
        analyses = []
        
        # Pour chaque métrique, identifier le meilleur algorithme
        for problem in df_success['problem'].unique():
            problem_data = df_success[df_success['problem'] == problem]
            
            if problem_data.empty:
                continue
            
            # Meilleur temps
            best_time = problem_data.groupby('algorithm')['time_ms'].mean().idxmin()
            best_time_value = problem_data.groupby('algorithm')['time_ms'].mean().min()
            
            # Meilleure mémoire
            best_memory = problem_data.groupby('algorithm')['memory_kb'].mean().idxmin()
            best_memory_value = problem_data.groupby('algorithm')['memory_kb'].mean().min()
            
            # Moins de nœuds visités
            best_nodes = problem_data.groupby('algorithm')['nodes_visited'].mean().idxmin()
            best_nodes_value = problem_data.groupby('algorithm')['nodes_visited'].mean().min()
            
            analyses.append({
                'Problème': problem,
                'Meilleur Temps': f"{best_time} ({best_time_value:.2f}ms)",
                'Meilleure Mémoire': f"{best_memory} ({best_memory_value:.0f}Ko)",
                'Moins de Nœuds': f"{best_nodes} ({best_nodes_value:.0f})",
            })
        
        return pd.DataFrame(analyses)
    
    def generate_markdown_report(self, output_file=None):
        """Génère un rapport au format Markdown"""
        if output_file is None:
            output_file = self.output_file
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # En-tête
            f.write("# Rapport de Benchmarking\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write("---\n\n")
            
            # Résumé des données
            f.write("## Vue d'Ensemble\n\n")
            f.write(f"- **Nombre total de tests:** {len(self.df)}\n")
            f.write(f"- **Tests réussis:** {self.df['success'].sum()} ({self.df['success'].mean()*100:.1f}%)\n")
            f.write(f"- **Algorithmes testés:** {self.df['algorithm'].nunique()}\n")
            f.write(f"- **Problèmes testés:** {self.df['problem'].nunique()}\n\n")
            
            # Statistiques résumées
            f.write("## Statistiques Résumées\n\n")
            summary = self.generate_summary_statistics()
            f.write(summary.to_markdown(index=False))
            f.write("\n\n")
            
            # Analyse des forces
            f.write("## Analyse Comparative\n\n")
            strengths = self.analyze_algorithm_strengths()
            f.write(strengths.to_markdown(index=False))
            f.write("\n\n")
            
            # Graphiques
            f.write("## Visualisations\n\n")
            f.write(f"![Temps d'exécution](../../visuals/{self.base_name}/time_comparison.png)\n\n")
            f.write(f"![Utilisation mémoire](../../visuals/{self.base_name}/memory_comparison.png)\n\n")
            f.write(f"![Nœuds explorés](../../visuals/{self.base_name}/nodes_comparison.png)\n\n")
            f.write(f"![Taux de succès](../../visuals/{self.base_name}/success_rate.png)\n\n")
            
            f.write("\n---\n\n")
            f.write("[Voir les détails de chaque instance](details.md)\n\n")
            f.write("*Rapport généré automatiquement*\n")
        
        print(f"Rapport généré: {output_file}")
    
    def generate_details_report(self, output_file=None):
        """Génère un rapport détaillé de chaque instance"""
        if output_file is None:
            output_file = self.details_file
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Trier les résultats par problème, algorithme, et succès
        sorted_results = sorted(
            self.results_raw,
            key=lambda x: (x['problem'], x['algorithm'], not x['success'], x['instance_id'])
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # En-tête
            f.write("# Détails des Instances\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write("[Retour au rapport principal](index.md)\n\n")
            f.write("---\n\n")
            
            # Grouper par problème
            current_problem = None
            current_algorithm = None
            
            for result in sorted_results:
                problem = result['problem']
                algorithm = result['algorithm']
                
                # Nouveau problème
                if problem != current_problem:
                    current_problem = problem
                    current_algorithm = None
                    f.write(f"\n## {problem}\n\n")
                
                # Nouvel algorithme dans ce problème
                if algorithm != current_algorithm:
                    current_algorithm = algorithm
                    f.write(f"\n### {algorithm}\n\n")
                    
                    # Statistiques pour cet algorithme sur ce problème
                    algo_results = [r for r in sorted_results 
                                   if r['problem'] == problem and r['algorithm'] == algorithm]
                    success_count = sum(1 for r in algo_results if r['success'])
                    total_count = len(algo_results)
                    f.write(f"**Taux de succès:** {success_count}/{total_count} ({success_count/total_count*100:.1f}%)\n\n")
                
                # Détails de l'instance
                instance_id = result['instance_id']
                success = result['success']
                metrics = result['metrics']
                error = result.get('error', None)
                initial_state = result.get('initial_state', None)
                
                status_emoji = "✅" if success else "❌"
                f.write(f"#### {status_emoji} Instance #{instance_id}\n\n")
                
                if success:
                    f.write("| Métrique | Valeur |\n")
                    f.write("|----------|--------|\n")
                    f.write(f"| **Temps** | {metrics['time_ms']:.2f} ms |\n")
                    f.write(f"| **Mémoire** | {metrics['memory_kb']:,} Ko |\n")
                    f.write(f"| **Nœuds visités** | {metrics['nodes_visited']:,} |\n")
                    f.write(f"| **Nœuds générés** | {metrics['nodes_generated']:,} |\n")
                    f.write(f"| **Longueur solution** | {metrics['solution_length']} |\n")
                    f.write(f"| **Taille frontière max** | {metrics['max_frontier_size']:,} |\n")
                else:
                    f.write(f"**Erreur:** {error if error else 'Pas de solution trouvée'}\n\n")
                    f.write("| Métrique | Valeur |\n")
                    f.write("|----------|--------|\n")
                    f.write(f"| **Temps écoulé** | {metrics['time_ms']:.2f} ms |\n")
                    f.write(f"| **Nœuds visités** | {metrics['nodes_visited']:,} |\n")
                
                if initial_state:
                    f.write("\n<details>\n")
                    f.write("<summary>État initial</summary>\n\n")
                    f.write("```\n")
                    f.write(initial_state)
                    f.write("\n```\n\n")
                    f.write("</details>\n")
                
                f.write("\n---\n\n")
            
            f.write("\n[Retour au rapport principal](index.md)\n")
        
        print(f"Rapport détaillé généré: {output_file}")



def main():
    import sys
    import glob
    
    target = 'results/benchmark_results.json'
    if len(sys.argv) > 1:
        target = sys.argv[1]
    
    print("Génération du Rapport de Benchmarking...")
    
    # Vérifier si c'est un dossier
    target_path = Path(target)
    json_files = []
    
    if target_path.is_dir():
        # Traiter tous les fichiers JSON du dossier
        json_files = list(target_path.glob('*.json'))
        if not json_files:
            print(f"Warning: Aucun fichier JSON trouvé dans {target}")
            sys.exit(1)
        print(f"Trouvé {len(json_files)} fichier(s) JSON à traiter...\n")
    elif target_path.is_file():
        json_files = [target_path]
    else:
        print(f"Error: {target} non trouvé")
        sys.exit(1)
    
    # Traiter chaque fichier JSON
    success_count = 0
    for json_file in json_files:
        try:
            print(f"\nGénération de {json_file.name}...")
            generator = ReportGenerator(str(json_file))
            generator.generate_markdown_report()
            generator.generate_details_report()
            success_count += 1
        except FileNotFoundError:
            print(f"Error: {json_file} non trouvé")
        except Exception as e:
            print(f"Error lors du traitement de {json_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\n{success_count}/{len(json_files)} fichier(s) traité(s)")


if __name__ == '__main__':
    main()
