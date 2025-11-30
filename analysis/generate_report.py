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
    
    def get_combined_markdown(self, include_details=False, analyses_file=None):
        """Retourne le contenu markdown combiné pour l'export PDF
        
        Args:
            include_details: Si True, inclut les détails des instances à la fin
            analyses_file: Chemin vers le fichier analyses.md à inclure
        """
        # Générer le contenu du rapport principal en mémoire
        content = []
        
        # Page de garde
        content.append("\\begin{titlepage}\n")
        content.append("\\centering\n")
        content.append("\\vspace*{3cm}\n")
        content.append("{\\Huge\\bfseries Rapport de Benchmarking\\par}\n")
        content.append("\\vspace{1cm}\n")
        content.append("{\\Large Analyse des Algorithmes de Recherche\\par}\n")
        content.append("\\vspace{2cm}\n")
        content.append(f"{{\\large {self.base_name}\\par}}\n")
        content.append("\\vspace{1cm}\n")
        content.append(f"{{\\large {datetime.now().strftime('%d/%m/%Y')}\\par}}\n")
        content.append("\\vfill\n")
        content.append("{\\normalsize Généré automatiquement par le framework de benchmarking\\par}\n")
        content.append("\\end{titlepage}\n")
        content.append("\n")
        
        # Page vide
        content.append("\\newpage\n")
        content.append("\\thispagestyle{empty}\n")
        content.append("\\mbox{}\n")
        content.append("\\newpage\n")
        content.append("\n")
        
        # Table des matières (générée par pandoc avec --toc)
        
        # Section Analyse (depuis analyses.md)
        if analyses_file:
            analyses_path = Path(analyses_file)
            if analyses_path.exists():
                with open(analyses_path, 'r', encoding='utf-8') as f:
                    analyses_content = f.read().strip()
                if analyses_content:
                    content.append("\n\\newpage\n")
                    content.append(analyses_content)
                    content.append("\n")
        
        # En-tête du rapport
        content.append("\n\\newpage\n")
        content.append("# Résultats du Benchmarking\n")
        content.append(f"**Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        content.append(f"**Fichier:** {self.base_name}\n")
        content.append("\n---\n")
        
        # Résumé des données
        content.append("\n## Vue d'Ensemble\n")
        content.append(f"- **Nombre total de tests:** {len(self.df)}\n")
        content.append(f"- **Tests réussis:** {self.df['success'].sum()} ({self.df['success'].mean()*100:.1f}%)\n")
        content.append(f"- **Algorithmes testés:** {self.df['algorithm'].nunique()}\n")
        content.append(f"- **Problèmes testés:** {self.df['problem'].nunique()}\n")
        
        # Statistiques résumées
        content.append("\n## Statistiques Résumées\n")
        summary = self.generate_summary_statistics()
        content.append(summary.to_markdown(index=False))
        content.append("\n")
        
        # Analyse des forces
        content.append("\n## Analyse Comparative\n")
        strengths = self.analyze_algorithm_strengths()
        content.append(strengths.to_markdown(index=False))
        content.append("\n")
        
        # Graphiques
        content.append("\n\\newpage\n")
        content.append("\n# Visualisations\n")
        
        # Liste des graphiques disponibles avec descriptions
        graphics = [
            ("time_comparison.png", "Comparaison des Temps d'Exécution"),
            ("memory_comparison.png", "Comparaison de l'Utilisation Mémoire"),
            ("nodes_comparison.png", "Comparaison des Nœuds Visités"),
            ("success_rate.png", "Taux de Succès par Algorithme"),
            ("heatmap_time.png", "Heatmap des Temps d'Exécution"),
            ("size_scaling.png", "Évolution selon la Taille du Problème"),
        ]
        
        for filename, title in graphics:
            img_path = self.visuals_dir / filename
            if img_path.exists():
                content.append(f"\n## {title}\n\n")
                # Utiliser un chemin absolu pour pandoc
                abs_path = img_path.resolve()
                # Forcer l'image à rester en place avec l'attribut width
                content.append(f"![{title}]({abs_path}){{ width=100% }}\n")
                content.append("\n\\newpage\n")
        
        # Détails des instances (optionnel, à la fin)
        if include_details:
            content.append("\n\\newpage\n")
            content.append("\n# Détails des Instances\n")
            
            # Trier les résultats
            sorted_results = sorted(
                self.results_raw,
                key=lambda x: (x['problem'], x['algorithm'], not x['success'], x['instance_id'])
            )
            
            current_problem = None
            current_algorithm = None
            
            for result in sorted_results:
                problem = result['problem']
                algorithm = result['algorithm']
                
                if problem != current_problem:
                    current_problem = problem
                    current_algorithm = None
                    content.append(f"\n## {problem}\n")
                
                if algorithm != current_algorithm:
                    current_algorithm = algorithm
                    content.append(f"\n### {algorithm}\n")
                    
                    algo_results = [r for r in sorted_results 
                                   if r['problem'] == problem and r['algorithm'] == algorithm]
                    success_count = sum(1 for r in algo_results if r['success'])
                    total_count = len(algo_results)
                    content.append(f"**Taux de succès:** {success_count}/{total_count} ({success_count/total_count*100:.1f}%)\n")
                
                instance_id = result['instance_id']
                success = result['success']
                metrics = result['metrics']
                error = result.get('error', None)
                
                status = "[OK]" if success else "[ECHEC]"
                content.append(f"\n#### {status} Instance #{instance_id}\n")
                
                if success:
                    content.append("| Métrique | Valeur |\n")
                    content.append("|----------|--------|\n")
                    content.append(f"| Temps | {metrics['time_ms']:.2f} ms |\n")
                    content.append(f"| Mémoire | {metrics['memory_kb']:,} Ko |\n")
                    content.append(f"| Nœuds visités | {metrics['nodes_visited']:,} |\n")
                    content.append(f"| Longueur solution | {metrics['solution_length']} |\n")
                else:
                    content.append(f"**Erreur:** {error if error else 'Pas de solution trouvée'}\n")
        
        return "".join(content)
    
    def get_simple_markdown(self, include_details=False):
        """Retourne le contenu markdown simplifié (sans page de garde) pour les rapports combinés
        
        Args:
            include_details: Si True, inclut les détails des instances à la fin
        """
        content = []
        
        # Vue d'ensemble
        content.append(f"\n**Nombre total de tests:** {len(self.df)}\n")
        content.append(f"**Tests réussis:** {self.df['success'].sum()} ({self.df['success'].mean()*100:.1f}%)\n")
        content.append(f"**Algorithmes testés:** {self.df['algorithm'].nunique()}\n")
        content.append(f"**Problèmes testés:** {self.df['problem'].nunique()}\n")
        
        # Statistiques résumées
        content.append("\n### Statistiques\n")
        summary = self.generate_summary_statistics()
        content.append(summary.to_markdown(index=False))
        content.append("\n")
        
        # Analyse des forces
        content.append("\n### Analyse Comparative\n")
        strengths = self.analyze_algorithm_strengths()
        content.append(strengths.to_markdown(index=False))
        content.append("\n")
        
        # Graphiques
        graphics = [
            ("time_comparison.png", "Temps d'Exécution"),
            ("memory_comparison.png", "Utilisation Mémoire"),
            ("nodes_comparison.png", "Nœuds Visités"),
            ("success_rate.png", "Taux de Succès"),
        ]
        
        for filename, title in graphics:
            img_path = self.visuals_dir / filename
            if img_path.exists():
                content.append(f"\n### {title}\n\n")
                abs_path = img_path.resolve()
                content.append(f"![{title}]({abs_path}){{ width=90% }}\n")
                content.append("\n\\newpage\n")
        
        # Détails des instances (optionnel)
        if include_details:
            content.append("\n### Détails des Instances\n")
            
            sorted_results = sorted(
                self.results_raw,
                key=lambda x: (x['problem'], x['algorithm'], not x['success'], x['instance_id'])
            )
            
            current_problem = None
            current_algorithm = None
            
            for result in sorted_results:
                problem = result['problem']
                algorithm = result['algorithm']
                
                if problem != current_problem:
                    current_problem = problem
                    current_algorithm = None
                    content.append(f"\n#### {problem}\n")
                
                if algorithm != current_algorithm:
                    current_algorithm = algorithm
                    algo_results = [r for r in sorted_results 
                                   if r['problem'] == problem and r['algorithm'] == algorithm]
                    success_count = sum(1 for r in algo_results if r['success'])
                    total_count = len(algo_results)
                    content.append(f"\n**{algorithm}:** {success_count}/{total_count} succès\n")
        
        return "".join(content)


def main():
    import sys
    
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
    
    print(f"\n{success_count}/{len(json_files)} fichier(s) traité(s)")


if __name__ == '__main__':
    main()
