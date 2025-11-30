"""
Script de génération de PDF à partir des rapports markdown
Utilise pandoc pour convertir les rapports en PDF
"""

import subprocess
import shutil
import os
import tempfile
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Import du générateur de rapport pour réutiliser la classe
from generate_report import ReportGenerator


def check_pandoc():
    """Vérifie que pandoc est installé"""
    if not shutil.which('pandoc'):
        print("Erreur: pandoc n'est pas installé ou non trouvé dans le PATH")
        print("Installez pandoc depuis: https://pandoc.org/installing.html")
        return False
    return True


def generate_pdf_from_markdown(markdown_content, output_path):
    """
    Génère un PDF à partir de contenu markdown en utilisant pandoc.
    
    Args:
        markdown_content: Contenu markdown à convertir
        output_path: Chemin du fichier PDF de sortie
    
    Returns:
        True si succès, False sinon
    """
    if not check_pandoc():
        return False
    
    # Créer un fichier temporaire pour le markdown
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp:
        tmp.write(markdown_content)
        tmp_path = tmp.name
    
    # S'assurer que le dossier de sortie existe
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Options pandoc de base (sans --toc car on le place manuellement)
        base_cmd = [
            'pandoc',
            tmp_path,
            '-o', str(output_path),
            '-V', 'geometry:margin=2cm',
            '-V', 'fontsize=11pt',
            '-V', 'documentclass=article'
        ]
        
        # Essayer avec xelatex d'abord (meilleur support Unicode)
        cmd = base_cmd.copy() + ['--pdf-engine=xelatex', '-V', 'mainfont=DejaVu Sans']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Réessayer avec xelatex sans police spécifique
            cmd = base_cmd.copy() + ['--pdf-engine=xelatex']
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Dernier essai avec pdflatex
            cmd = base_cmd.copy() + ['--pdf-engine=pdflatex']
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Erreur pandoc: {result.stderr}")
            return False
            
    finally:
        # Nettoyer le fichier temporaire
        os.unlink(tmp_path)


def generate_single_pdf(json_file, output_path=None, include_details=False, presentation_file=None):
    """
    Génère un PDF à partir d'un seul fichier JSON.
    
    Args:
        json_file: Chemin vers le fichier JSON
        output_path: Chemin du fichier PDF de sortie (optionnel)
        include_details: Inclure les détails des instances à la fin
        presentation_file: Chemin vers le fichier presentation.md à inclure
    
    Returns:
        True si succès, False sinon
    """
    json_path = Path(json_file)
    
    if output_path is None:
        output_path = Path('results/reports') / f"{json_path.stem}_report.pdf"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        generator = ReportGenerator(str(json_file))
        markdown_content = generator.get_combined_markdown(
            include_details=include_details,
            presentation_file=presentation_file
        )
        
        if generate_pdf_from_markdown(markdown_content, output_path):
            print(f"PDF généré: {output_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Erreur lors du traitement de {json_file}: {e}")
        return False


def generate_combined_pdf(json_files, output_path, include_details=False, presentation_file=None):
    """
    Génère un PDF combiné à partir de plusieurs fichiers JSON.
    
    Args:
        json_files: Liste de chemins vers les fichiers JSON
        output_path: Chemin du fichier PDF de sortie
        include_details: Inclure les détails des instances à la fin
        presentation_file: Chemin vers le fichier presentation.md à inclure
    
    Returns:
        True si succès, False sinon
    """
    if not check_pandoc():
        return False
    
    all_content = []
    
    # Page de garde
    all_content.append("\\begin{titlepage}\n")
    all_content.append("\\centering\n")
    all_content.append("\\vspace*{3cm}\n")
    all_content.append("{\\Huge\\bfseries Rapport de Benchmarking\\par}\n")
    all_content.append("\\vspace{1cm}\n")
    all_content.append("{\\Large Analyse des Algorithmes de Recherche\\par}\n")
    all_content.append("\\vspace{2cm}\n")
    all_content.append("{\\large BFS, DFS, ID, A*, IDA*\\par}\n")
    all_content.append("\\vspace{1cm}\n")
    all_content.append(f"{{\\large {datetime.now().strftime('%d/%m/%Y')}\\par}}\n")
    all_content.append("\\vfill\n")
    all_content.append("{\\normalsize \\par}\n")
    all_content.append("\\end{titlepage}\n")
    all_content.append("\n")
    
    # Page vide
    all_content.append("\\newpage\n")
    all_content.append("\\thispagestyle{empty}\n")
    all_content.append("\\mbox{}\n")
    all_content.append("\\newpage\n")
    all_content.append("\n")
    
    # Table des matières (placée manuellement après la page vide)
    all_content.append("\\renewcommand{\\contentsname}{Table des Matières}\n")
    all_content.append("\\tableofcontents\n")
    all_content.append("\\newpage\n")
    all_content.append("\n")
    
    # Section Analyse (depuis presentation.md)
    if presentation_file:
        presentation_path = Path(presentation_file)
        if presentation_path.exists():
            with open(presentation_path, 'r', encoding='utf-8') as f:
                presentation_content = f.read().strip()
            if presentation_content:
                all_content.append("\n\\newpage\n")
                all_content.append(presentation_content)
                all_content.append("\n")
    
    # Résultats
    all_content.append("\n\\newpage\n")
    all_content.append("# Résultats des Benchmarks\n")
    all_content.append(f"**Date de génération:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    all_content.append(f"**Nombre de fichiers:** {len(json_files)}\n")
    all_content.append("\n---\n")
    
    processed = 0
    for i, json_file in enumerate(json_files):
        try:
            generator = ReportGenerator(str(json_file))
            # Pour les rapports combinés, on ne veut pas la page de garde individuelle
            # On génère directement les statistiques
            content = generator.get_simple_markdown(include_details=include_details)
            
            # Ajouter un saut de page entre les rapports
            if i > 0:
                all_content.append("\n\\newpage\n")
            
            all_content.append(f"\n## {json_file.stem}\n")
            all_content.append(content)
            processed += 1
            
        except Exception as e:
            print(f"Erreur lors du traitement de {json_file}: {e}")
            continue
    
    if processed == 0:
        print("Aucun fichier traité avec succès")
        return False
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if generate_pdf_from_markdown("".join(all_content), output_path):
        print(f"PDF combiné généré: {output_path}")
        return True
    return False


def generate_from_markdown_files(markdown_files, output_path):
    """
    Génère un PDF à partir de fichiers markdown existants.
    
    Args:
        markdown_files: Liste de chemins vers les fichiers markdown
        output_path: Chemin du fichier PDF de sortie
    
    Returns:
        True si succès, False sinon
    """
    if not check_pandoc():
        return False
    
    all_content = []
    all_content.append("# Rapport de Benchmarking\n")
    all_content.append(f"**Date de génération:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    all_content.append("\n---\n")
    
    for i, md_file in enumerate(markdown_files):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if i > 0:
                all_content.append("\n\\newpage\n")
            
            all_content.append(content)
            
        except Exception as e:
            print(f"Erreur lors de la lecture de {md_file}: {e}")
            continue
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if generate_pdf_from_markdown("".join(all_content), output_path):
        print(f"PDF généré: {output_path}")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Génère des PDF à partir de fichiers JSON ou markdown de benchmarking.',
        epilog='Exemples:\n'
               '  python generate_pdf.py results/benchmark.json\n'
               '  python generate_pdf.py results/ -o combined.pdf\n'
               '  python generate_pdf.py results/reports/*/index.md --markdown -o report.pdf\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('targets', nargs='+',
                        help='Fichier(s) JSON/markdown ou dossier contenant les fichiers')
    parser.add_argument('-o', '--output', default=None,
                        help='Chemin du fichier PDF de sortie')
    parser.add_argument('--markdown', '-m', action='store_true',
                        help='Traiter les fichiers comme du markdown au lieu de JSON')
    parser.add_argument('--details', '-d', action='store_true',
                        help='Inclure les détails des instances à la fin du PDF')
    parser.add_argument('--presentation', '-a', default=None,
                        help='Chemin vers le fichier presentation.md à inclure après la table des matières')
    
    args = parser.parse_args()
    
    print("Génération du PDF...")
    
    # Collecter tous les fichiers à traiter
    files = []
    for target in args.targets:
        target_path = Path(target)
        
        if target_path.is_dir():
            if args.markdown:
                files.extend(target_path.glob('**/*.md'))
            else:
                files.extend(target_path.glob('*.json'))
        elif target_path.is_file():
            # Ignorer les fichiers PDF
            if target_path.suffix.lower() != '.pdf':
                files.append(target_path)
        elif '*' in target:
            # Support des globs
            import glob
            files.extend(Path(f) for f in glob.glob(target) if not f.endswith('.pdf'))
        else:
            print(f"Warning: {target} non trouvé")
    
    if not files:
        print("Aucun fichier trouvé à traiter")
        sys.exit(1)
    
    print(f"Trouvé {len(files)} fichier(s) à traiter...")
    
    # Déterminer le chemin de sortie
    if args.output:
        output_path = Path(args.output)
    elif len(files) == 1:
        output_path = Path('results/reports') / f"{files[0].stem}_report.pdf"
    else:
        output_path = Path('results/reports') / 'combined_report.pdf'
    
    # Générer le PDF
    if args.markdown:
        success = generate_from_markdown_files(files, output_path)
    elif len(files) == 1:
        success = generate_single_pdf(files[0], output_path, 
                                      include_details=args.details,
                                      presentation_file=args.presentation)
    else:
        success = generate_combined_pdf(files, output_path, 
                                        include_details=args.details,
                                        presentation_file=args.presentation)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
