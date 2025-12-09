"""
back_end.py
Module contenant toutes les fonctions de calcul pour la planification 
d'un réseau cellulaire GSM
"""

import numpy as np
import json

def load_params(filename='params.json'):
    """
    Charge les paramètres depuis un fichier JSON
    
    Args:
        filename: nom du fichier JSON
    Returns:
        dict: dictionnaire contenant les paramètres
    """
    try:
        with open(filename, 'r') as f:
            params = json.load(f)
        return params
    except FileNotFoundError:
        print(f"Fichier {filename} introuvable. Utilisation des paramètres par défaut.")
        return get_default_params()

def save_params(params, filename='params.json'):
    """
    Sauvegarde les paramètres dans un fichier JSON
    
    Args:
        params: dictionnaire des paramètres
        filename: nom du fichier JSON
    """
    with open(filename, 'w') as f:
        json.dump(params, f, indent=4)
    print(f"Paramètres sauvegardés dans {filename}")

def get_default_params():
    """
    Retourne les paramètres par défaut
    """
    return {
        "P_BTS_dBm": 43,
        "P_MS_dBm": 23,
        "P_sens_dBm": -100,
        "N_f": 124,
        "f_port_MHz": 900,
        "N": 7,
        "SIR_min_dB": 17,
        "Dst_ab": 20,
        "T_act": 0.10,
        "Pathloss_exp": 3.5,
        "d0_km": 1
    }

def calculate_max_path_loss(P_tx_dBm, P_sens_dBm, G_ant_dB=2):
    """
    Calcule la perte de trajet maximale admissible
    
    Args:
        P_tx_dBm: puissance d'émission (dBm)
        P_sens_dBm: sensibilité du récepteur (dBm)
        G_ant_dB: gain total des antennes (dB)
    Returns:
        float: perte de trajet maximale (dB)
    """
    # Budget de liaison: P_tx + G_ant - Path_loss ≥ P_sens
    # donc: Path_loss_max = P_tx + G_ant - P_sens
    return P_tx_dBm + G_ant_dB - P_sens_dBm

def calculate_cell_radius(P_tx_dBm, P_sens_dBm, pathloss_exp, d0_km=1, G_ant_dB=2):
    """
    Calcule le rayon maximal d'une cellule en utilisant le modèle log-distance
    
    Modèle: PL(d) = PL(d0) + 10*n*log10(d/d0)
    où PL(d0) ≈ 0 pour simplifier
    
    Args:
        P_tx_dBm: puissance d'émission (dBm)
        P_sens_dBm: sensibilité du récepteur (dBm)
        pathloss_exp: exposant de perte de propagation
        d0_km: distance de référence (km)
        G_ant_dB: gain des antennes (dB)
    Returns:
        float: rayon maximal de la cellule (km)
    """
    PL_max = calculate_max_path_loss(P_tx_dBm, P_sens_dBm, G_ant_dB)
    
    # PL(d) = 10*n*log10(d/d0)
    # d = d0 * 10^(PL/(10*n))
    R = d0_km * (10 ** (PL_max / (10 * pathloss_exp)))
    
    return R

def calculate_reuse_distance(R, N):
    """
    Calcule la distance de réutilisation des fréquences
    
    Pour un motif hexagonal: D = R * sqrt(3*N)
    
    Args:
        R: rayon de la cellule (km)
        N: taille du motif cellulaire
    Returns:
        float: distance de réutilisation (km)
    """
    return R * np.sqrt(3 * N)

def calculate_SIR(R, D, pathloss_exp):
    """
    Calcule le rapport Signal/Interférence (S/I)
    
    En considérant seulement le premier anneau d'interféreurs (6 cellules)
    S/I = (D/R)^n / 6
    
    Args:
        R: rayon de la cellule (km)
        D: distance de réutilisation (km)
        pathloss_exp: exposant de perte de propagation
    Returns:
        float: S/I en dB
    """
    # S/I linéaire
    SIR_linear = ((D / R) ** pathloss_exp) / 6
    
    # Conversion en dB
    SIR_dB = 10 * np.log10(SIR_linear)
    
    return SIR_dB

def calculate_channels_per_cell(N_f, N):
    """
    Calcule le nombre de canaux par cellule
    
    Args:
        N_f: nombre total de canaux disponibles
        N: taille du motif cellulaire
    Returns:
        int: nombre de canaux par cellule
    """
    return N_f // N

def calculate_cell_area(R):
    """
    Calcule la surface d'une cellule hexagonale
    
    Surface hexagone = (3*sqrt(3)/2) * R^2
    
    Args:
        R: rayon de la cellule (km)
    Returns:
        float: surface de la cellule (km²)
    """
    return (3 * np.sqrt(3) / 2) * (R ** 2)

def calculate_subscribers_per_cell(R, Dst_ab):
    """
    Calcule le nombre d'abonnés par cellule
    
    Args:
        R: rayon de la cellule (km)
        Dst_ab: densité d'abonnés (abonnés/km²)
    Returns:
        float: nombre d'abonnés par cellule
    """
    area = calculate_cell_area(R)
    return area * Dst_ab

def calculate_active_users(subscribers, T_act):
    """
    Calcule le nombre d'utilisateurs actifs simultanément
    
    Args:
        subscribers: nombre d'abonnés
        T_act: taux d'activité
    Returns:
        float: nombre d'utilisateurs actifs
    """
    return subscribers * T_act

def adjust_radius_for_SIR(P_BTS_dBm, P_MS_dBm, P_sens_dBm, N, SIR_min_dB, 
                          pathloss_exp, d0_km=1):
    """
    Ajuste le rayon de cellule pour respecter le critère S/I minimum
    
    Args:
        P_BTS_dBm: puissance BTS (dBm)
        P_MS_dBm: puissance MS (dBm)
        P_sens_dBm: sensibilité (dBm)
        N: taille du motif
        SIR_min_dB: S/I minimum requis (dB)
        pathloss_exp: exposant de propagation
        d0_km: distance de référence
    Returns:
        tuple: (R_final, D, SIR_obtained)
    """
    # Rayon maximal basé sur la couverture (downlink: BTS vers MS)
    R_coverage_downlink = calculate_cell_radius(P_BTS_dBm, P_sens_dBm, pathloss_exp, d0_km)
    
    # Rayon maximal basé sur la couverture (uplink: MS vers BTS)
    R_coverage_uplink = calculate_cell_radius(P_MS_dBm, P_sens_dBm, pathloss_exp, d0_km)
    
    # Le rayon est limité par le lien le plus faible
    R_coverage = min(R_coverage_downlink, R_coverage_uplink)
    
    # Distance de réutilisation
    D = calculate_reuse_distance(R_coverage, N)
    
    # S/I obtenu
    SIR_obtained = calculate_SIR(R_coverage, D, pathloss_exp)
    
    # Si S/I n'est pas satisfait, réduire R
    if SIR_obtained < SIR_min_dB:
        # S/I = 10*log10((D/R)^n / 6)
        # SIR_min = 10*log10((D/R)^n / 6)
        # (D/R)^n = 6 * 10^(SIR_min/10)
        # D = R * sqrt(3*N)
        # R^n * 3*N = R^n * (D/R)^n = D^n = R^n * 6 * 10^(SIR_min/10)
        # Besoin de réduire R
        
        # Formule: R = D / sqrt(3*N) où D est calculé pour satisfaire S/I
        # (D/R)^n / 6 = 10^(SIR_min/10)
        # D/R = (6 * 10^(SIR_min/10))^(1/n)
        # R = D / (6 * 10^(SIR_min/10))^(1/n)
        
        # Mais D = R*sqrt(3*N), donc:
        # R = R*sqrt(3*N) / (6 * 10^(SIR_min/10))^(1/n)
        # 1 = sqrt(3*N) / (6 * 10^(SIR_min/10))^(1/n)
        # (6 * 10^(SIR_min/10))^(1/n) = sqrt(3*N)
        
        ratio = (6 * (10 ** (SIR_min_dB / 10))) ** (1 / pathloss_exp)
        R_sir = R_coverage * np.sqrt(3 * N) / ratio
        
        R_final = min(R_coverage, R_sir)
    else:
        R_final = R_coverage
    
    # Recalculer avec le rayon final
    D_final = calculate_reuse_distance(R_final, N)
    SIR_final = calculate_SIR(R_final, D_final, pathloss_exp)
    
    return R_final, D_final, SIR_final

def run_complete_analysis(params):
    """
    Effectue une analyse complète du réseau
    
    Args:
        params: dictionnaire des paramètres
    Returns:
        dict: résultats de l'analyse
    """
    # Extraction des paramètres
    P_BTS_dBm = params['P_BTS_dBm']
    P_MS_dBm = params['P_MS_dBm']
    P_sens_dBm = params['P_sens_dBm']
    N_f = params['N_f']
    N = params['N']
    SIR_min_dB = params['SIR_min_dB']
    Dst_ab = params['Dst_ab']
    T_act = params['T_act']
    pathloss_exp = params['Pathloss_exp']
    d0_km = params['d0_km']
    
    # Calculs
    R, D, SIR = adjust_radius_for_SIR(P_BTS_dBm, P_MS_dBm, P_sens_dBm, 
                                       N, SIR_min_dB, pathloss_exp, d0_km)
    
    channels_per_cell = calculate_channels_per_cell(N_f, N)
    cell_area = calculate_cell_area(R)
    subscribers = calculate_subscribers_per_cell(R, Dst_ab)
    active_users = calculate_active_users(subscribers, T_act)
    
    # Résultats
    results = {
        'R_km': R,
        'D_km': D,
        'SIR_dB': SIR,
        'SIR_min_dB': SIR_min_dB,
        'SIR_ok': SIR >= SIR_min_dB,
        'cell_area_km2': cell_area,
        'channels_per_cell': channels_per_cell,
        'subscribers_per_cell': subscribers,
        'active_users_per_cell': active_users,
        'capacity_ok': active_users <= channels_per_cell
    }
    
    return results

def print_results(results, params):
    """
    Affiche les résultats de manière formatée
    """
    print("\n" + "="*60)
    print("RÉSULTATS DE LA PLANIFICATION DU RÉSEAU CELLULAIRE")
    print("="*60)
    
    print(f"\n📡 CONFIGURATION:")
    print(f"   Motif cellulaire (N): {params['N']}")
    print(f"   Canaux disponibles: {params['N_f']}")
    print(f"   Exposant de propagation: {params['Pathloss_exp']}")
    
    print(f"\n📏 DIMENSIONS:")
    print(f"   Rayon de cellule (R): {results['R_km']:.3f} km")
    print(f"   Distance de réutilisation (D): {results['D_km']:.3f} km")
    print(f"   Surface de cellule: {results['cell_area_km2']:.3f} km²")
    
    print(f"\n📶 INTERFÉRENCES:")
    print(f"   S/I minimum requis: {results['SIR_min_dB']:.1f} dB")
    print(f"   S/I obtenu: {results['SIR_dB']:.2f} dB")
    status = "✓ OK" if results['SIR_ok'] else "✗ INSUFFISANT"
    print(f"   Statut: {status}")
    
    print(f"\n👥 CAPACITÉ:")
    print(f"   Canaux par cellule: {results['channels_per_cell']}")
    print(f"   Abonnés par cellule: {results['subscribers_per_cell']:.0f}")
    print(f"   Utilisateurs actifs: {results['active_users_per_cell']:.1f}")
    capacity_status = "✓ OK" if results['capacity_ok'] else "✗ SURCHARGE"
    print(f"   Statut capacité: {capacity_status}")
    
    print("="*60 + "\n")