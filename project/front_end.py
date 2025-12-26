"""
front_end.py
Module de visualisation et d'interaction utilisateur pour la planification
d'un réseau cellulaire GSM
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import RegularPolygon
import back_end as be

def create_hexagon_grid(R, grid_size=7):
    """
    Crée une grille hexagonale de stations de base
    
    Args:
        R: rayon de la cellule (km)
        grid_size: taille de la grille (ex: 7 pour 7x7)
    Returns:
        list: liste de coordonnées (x, y) des centres de cellules
    """
    centers = []
    
    # Distance horizontale et verticale entre hexagones
    dx = R * np.sqrt(3)
    dy = R * 1.5
    
    # Générer la grille
    for row in range(grid_size):
        for col in range(grid_size):
            # Décalage pour les rangées impaires
            x = col * dx + (row % 2) * dx / 2
            y = row * dy
            centers.append((x, y))
    
    return centers

def assign_frequency_groups(centers, N):
    """
    Assigne des groupes de fréquences aux cellules selon le motif N
    
    Args:
        centers: liste des coordonnées des cellules
        N: taille du motif cellulaire
    Returns:
        list: liste des groupes de fréquences pour chaque cellule
    """
    frequency_groups = []
    
    for i, (x, y) in enumerate(centers):
        # Algorithme simple basé sur la position
        # Pour N=3: motif (0,1,2) se répète
        # Pour N=7: motif plus complexe
        
        if N == 3:
            group = i % 3
        elif N == 4:
            group = i % 4
        elif N == 7:
            # Motif hexagonal pour N=7
            group = i % 7
        elif N == 9:
            group = i % 9
        elif N == 12:
            group = i % 12
        else:
            group = i % N
        
        frequency_groups.append(group)
    
    return frequency_groups

def get_color_palette(N):
    """
    Génère une palette de couleurs pour N groupes de fréquences
    """
    if N <= 3:
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1'][:N]
    elif N <= 7:
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', 
                  '#98D8C8', '#F7DC6F', '#BB8FCE'][:N]
    elif N <= 12:
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', 
                  '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
                  '#F8B88B', '#A8E6CF', '#FFD3B6', '#C7CEEA'][:N]
    else:
        # Générer des couleurs automatiquement
        colors = plt.cm.tab20(np.linspace(0, 1, N))
    
    return colors

def plot_cellular_network(R, centers, frequency_groups, N, results, 
                          filename='cellular_network.png'):
    """
    Visualise le réseau cellulaire hexagonal
    
    Args:
        R: rayon des cellules (km)
        centers: liste des coordonnées des cellules
        frequency_groups: groupes de fréquences assignés
        N: taille du motif
        results: dictionnaire des résultats de calcul
        filename: nom du fichier de sortie
    """
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Palette de couleurs
    colors = get_color_palette(N)
    
    # Dessiner chaque cellule hexagonale
    for (x, y), freq_group in zip(centers, frequency_groups):
        hexagon = RegularPolygon(
            (x, y), 
            numVertices=6, 
            radius=R,
            orientation=0,
            facecolor=colors[freq_group],
            edgecolor='black',
            linewidth=1.5,
            alpha=0.6
        )
        ax.add_patch(hexagon)
        
        # Ajouter un marqueur pour la BTS
        ax.plot(x, y, 'k^', markersize=8, markerfacecolor='red', 
                markeredgecolor='black', markeredgewidth=1)
        
        # Ajouter le numéro de groupe de fréquence
        ax.text(x, y-0.3*R, f'F{freq_group}', 
                ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Configuration des axes
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('Distance (km)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
    
    # Titre avec informations
    title = f'Plan Cellulaire GSM - Motif N={N}\n'
    title += f'R = {R:.3f} km | D = {results["D_km"]:.3f} km | '
    title += f'S/I = {results["SIR_dB"]:.2f} dB'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Légende
    legend_elements = []
    for i in range(N):
        legend_elements.append(
            patches.Patch(facecolor=colors[i], edgecolor='black', 
                         label=f'Groupe fréquence {i}')
        )
    legend_elements.append(
        plt.Line2D([0], [0], marker='^', color='w', 
                   markerfacecolor='red', markeredgecolor='black',
                   markersize=10, label='BTS (Station de base)')
    )
    
    ax.legend(handles=legend_elements, loc='upper left', 
              bbox_to_anchor=(1.02, 1), fontsize=10)
    
    # Informations supplémentaires
    info_text = f'Canaux/cellule: {results["channels_per_cell"]}\n'
    info_text += f'Abonnés/cellule: {results["subscribers_per_cell"]:.0f}\n'
    info_text += f'Utilisateurs actifs: {results["active_users_per_cell"]:.1f}\n'
    info_text += f'S/I min requis: {results["SIR_min_dB"]:.1f} dB'
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Figure sauvegardée: {filename}")
    plt.show()

def compare_patterns(params_base, N_values=[3, 4, 7, 9]):
    """
    Compare différents motifs cellulaires
    
    Args:
        params_base: paramètres de base
        N_values: liste des valeurs de N à comparer
    Returns:
        dict: résultats comparatifs
    """
    comparison_results = {}
    
    print("\n" + "="*80)
    print("COMPARAISON DES MOTIFS CELLULAIRES")
    print("="*80)
    
    for N in N_values:
        params = params_base.copy()
        params['N'] = N
        results = be.run_complete_analysis(params)
        comparison_results[N] = results
        
        print(f"\n📊 MOTIF N = {N}:")
        print(f"   R = {results['R_km']:.3f} km | D = {results['D_km']:.3f} km")
        print(f"   S/I = {results['SIR_dB']:.2f} dB (min: {results['SIR_min_dB']:.1f} dB)")
        print(f"   Canaux/cellule: {results['channels_per_cell']}")
        print(f"   Utilisateurs actifs: {results['active_users_per_cell']:.1f}")
        print(f"   Statut S/I: {'✓' if results['SIR_ok'] else '✗'}")
        print(f"   Statut capacité: {'✓' if results['capacity_ok'] else '✗'}")
    
    print("="*80 + "\n")
    return comparison_results

def create_comparison_table(comparison_results):
    """
    Crée un tableau comparatif formaté
    """
    print("\n" + "="*100)
    print(f"{'N':<5} {'R (km)':<10} {'D (km)':<10} {'S/I (dB)':<12} "
          f"{'Canaux':<10} {'Util.actifs':<15} {'S/I OK':<10} {'Cap OK':<10}")
    print("="*100)
    
    for N, res in sorted(comparison_results.items()):
        sir_status = '✓' if res['SIR_ok'] else '✗'
        cap_status = '✓' if res['capacity_ok'] else '✗'
        
        print(f"{N:<5} {res['R_km']:<10.3f} {res['D_km']:<10.3f} "
              f"{res['SIR_dB']:<12.2f} {res['channels_per_cell']:<10} "
              f"{res['active_users_per_cell']:<15.1f} {sir_status:<10} {cap_status:<10}")
    
    print("="*100 + "\n")

def interactive_menu():
    """
    Menu interactif pour l'utilisateur
    """
    print("\n" + "="*60)
    print("PLANIFICATION DE RÉSEAU CELLULAIRE GSM")
    print("="*60)
    print("1. Charger paramètres depuis params.json")
    print("2. Utiliser paramètres par défaut")
    print("3. Éditer paramètres manuellement")
    print("4. Quitter")
    print("="*60)
    
    choice = input("\nVotre choix (1-4): ").strip()
    
    if choice == '1':
        params = be.load_params()
    elif choice == '2':
        params = be.get_default_params()
    elif choice == '3':
        params = edit_params_interactive()
    else:
        print("Au revoir!")
        return None
    
    return params

def edit_params_interactive():
    """
    Permet d'éditer les paramètres de manière interactive
    """
    params = be.get_default_params()
    
    print("\n📝 Édition des paramètres (appuyez sur Entrée pour garder la valeur par défaut):")
    
    for key, default_value in params.items():
        user_input = input(f"{key} [{default_value}]: ").strip()
        if user_input:
            try:
                # Convertir au bon type
                if isinstance(default_value, int):
                    params[key] = int(user_input)
                else:
                    params[key] = float(user_input)
            except ValueError:
                print(f"Valeur invalide, conservation de {default_value}")
    
    # Demander si sauvegarder
    save = input("\nSauvegarder ces paramètres? (o/n): ").strip().lower()
    if save == 'o':
        filename = input("Nom du fichier [params.json]: ").strip()
        if not filename:
            filename = 'params.json'
        be.save_params(params, filename)
    
    return params

def main():
    """
    Fonction principale
    """
    # Choix de l'utilisateur
    params = interactive_menu()
    
    if params is None:
        return
    
    # Analyse complète
    print("\n🔄 Analyse en cours...")
    results = be.run_complete_analysis(params)
    be.print_results(results, params)
    
    # Vérification et recommandations
    if not results['SIR_ok']:
        print("⚠️  ATTENTION: Le critère S/I n'est pas satisfait!")
        print("   Solutions possibles:")
        print("   - Augmenter N (motif cellulaire)")
        print("   - Réduire le rayon R (plus de cellules)")
        print("   - Augmenter la puissance d'émission")
    
    if not results['capacity_ok']:
        print("⚠️  ATTENTION: Surcharge de capacité!")
        print("   Solutions possibles:")
        print("   - Réduire N (plus de canaux par cellule)")
        print("   - Réduire le rayon R (moins d'abonnés par cellule)")
    
    # Visualisation
    print("\n🎨 Génération de la visualisation...")
    grid_size = int(input("Taille de la grille (3, 5, 7): ").strip() or "7")
    centers = create_hexagon_grid(results['R_km'], grid_size)
    freq_groups = assign_frequency_groups(centers, params['N'])
    plot_cellular_network(results['R_km'], centers, freq_groups, 
                         params['N'], results)
    
    # Comparaison de motifs
    compare = input("\n🔍 Comparer avec d'autres motifs? (o/n): ").strip().lower()
    if compare == 'o':
        comparison = compare_patterns(params)
        create_comparison_table(comparison)

if __name__ == "__main__":
    main()