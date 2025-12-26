"""
Team: 
Bennouioua mohammed lamine
Gharbi zine eddine
"""

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

def compute_reuse_distance(R_km, N):
    """
    Calcule la distance de réutilisation des fréquences
    
    Pour un motif hexagonal: D = R * sqrt(3*N)
    
    Args:
        R_km: rayon de la cellule (km)
        N: taille du motif cellulaire
    Returns:
        float: distance de réutilisation (km)
    """
    return R_km * np.sqrt(3 * N)

def calculate_reuse_distance(R, N):
    """
    Alias pour compatibilité - appelle compute_reuse_distance
    """
    return compute_reuse_distance(R, N)

def compute_SIR(N, Pathloss_exp):
    """
    Calcule le rapport Signal/Interférence (S/I) en fonction du motif
    
    En considérant seulement le premier anneau d'interféreurs (6 cellules)
    S/I = (D/R)^n / 6
    Avec D = R * sqrt(3*N)
    Donc S/I = (sqrt(3*N))^n / 6
    
    Args:
        N: taille du motif cellulaire
        Pathloss_exp: exposant de perte de propagation
    Returns:
        float: S/I en dB
    """
    # D/R = sqrt(3*N) pour un motif hexagonal
    D_over_R = np.sqrt(3 * N)
    
    # S/I linéaire
    SIR_linear = (D_over_R ** Pathloss_exp) / 6
    
    # Conversion en dB
    SIR_dB = 10 * np.log10(SIR_linear)
    
    return SIR_dB

def calculate_SIR(R, D, pathloss_exp):
    """
    Calcule le rapport Signal/Interférence (S/I) avec R et D explicites
    (VERSION ORIGINALE - conservée pour compatibilité)
    
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

def distribute_carriers(N_f: int, N: int):
    """
    Répartit équitablement les N_f canaux fréquentiels entre les N cellules 
    d'un motif de réutilisation.

    Paramètres
    ----------
    N_f : int
        Nombre total de canaux fréquentiels disponibles dans le système.
        
    N : int
        Nombre de cellules dans le motif de réutilisation 

    Retourne
    --------
    carriers_cell : int
        Le nombre de porteuses attribuées à chaque cellule du motif.
        La répartition se fait de manière quasi uniforme :
            - division entière : N_f // N
            - +1 pour quelques cellules si N_f n'est pas divisible par N.
    """
    base_carriers = N_f // N
    remainder = N_f % N
    
    # Créer une liste avec la répartition des porteuses
    carriers_distribution = []
    for i in range(N):
        if i < remainder:
            carriers_distribution.append(base_carriers + 1)
        else:
            carriers_distribution.append(base_carriers)
    
    return carriers_distribution

def calculate_channels_per_cell(N_f, N):
    """
    Calcule le nombre de canaux par cellule (version simple - moyenne)
    
    Args:
        N_f: nombre total de canaux disponibles
        N: taille du motif cellulaire
    Returns:
        int: nombre de canaux par cellule
    """
    return N_f // N

def compute_cells_capacity(carriers: list,
                          Dst_ab: float,
                          T_act: float,
                          R_km: float):
    """
    Calcule :
      - la capacité physique (en Erlangs) par cellule
        -> 8 Erlangs par porteuse
      - le nombre d'abonnés actifs par cellule
        -> Dst_ab * T_act * Aire_cellule

    Parameters
    ----------
    carriers : list
        Nombre de porteuses par cellule du motif.
    Dst_ab : float
        Densité d'abonnés (abonnés / km²).
    T_act : float
        Taux d'activité des abonnés (Erlangs par abonné).
    R_km : float
        Rayon de la cellule (en km).

    Returns
    -------
    dict :
        {
            "canaux_par_cellule": [...],
            "abonnes_actifs_par_cellule": [...]
        }
    """
    canaux_par_cellule = []
    abonnes_par_cellule = []
    
    # Surface d'une cellule hexagonale
    cell_area = calculate_cell_area(R_km)
    
    for carrier_count in carriers:
        # Capacité en Erlangs: 8 Erlangs par porteuse
        capacity_erlangs = carrier_count * 8
        canaux_par_cellule.append(capacity_erlangs)
        
        # Nombre d'abonnés actifs dans cette cellule
        # Abonnés totaux = Densité × Surface
        # Abonnés actifs = Abonnés totaux × Taux_activité
        total_subscribers = Dst_ab * cell_area
        active_subscribers = total_subscribers * T_act
        abonnes_par_cellule.append(active_subscribers)
    
    return {
        "canaux_par_cellule": canaux_par_cellule,
        "abonnes_actifs_par_cellule": abonnes_par_cellule
    }

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

def compute_final_radius(P_tx_BTS_dBm: float,
                        P_tx_MS_dBm: float,
                        P_sens_MS_dBm: float,
                        P_sens_BTS_dBm: float,
                        Pathloss_exp: float,
                        d0_km: float,
                        carriers_cell: int,
                        density_ab: float,
                        activity_rate: float,
                        f_port_MHz: float) -> tuple:
    """
    Calcule le rayon final optimal d'une cellule, en tenant compte :
      - de la capacité (nombre d'abonnés actifs / canaux disponibles)
      - de la contrainte de couverture (sensibilité du récepteur)
      - de la contrainte SIR (réutilisation des fréquences)

    Paramètres
    ----------
    P_tx_BTS_dBm : float
        Puissance émission BTS (dBm).
    P_tx_MS_dBm : float
        Puissance émission mobile MS (dBm).
    P_sens_MS_dBm : float
        Sensibilité du récepteur mobile (dBm).
    P_sens_BTS_dBm : float
        Sensibilité du récepteur BTS (dBm).
    Pathloss_exp : float
        Exposant du modèle log-distance (2.7–4).
    d0_km : float
        Distance de référence en km.
    carriers_cell : int
        Nombre de porteuses par cellule du motif.
    density_ab : float
        Densité moyenne des abonnés (abonnés/km²).
    activity_rate : float
        Taux d'abonnés actifs simultanément.
    f_port_MHz: float
        Fréquence de port (MHz).

    Retourne
    --------
    tuple : (Rmax_coverage, Rmax_capacity, R_final)
        - Rmax_coverage en km : rayon max basé sur la couverture
        - Rmax_capacity en km : rayon max basé sur la capacité
        - R_final en km : rayon final optimal
    """
    G_ant_dB = 2  # Gain des antennes (hypothèse simplificatrice)
    
    # 1. Rayon maximal basé sur la couverture (DOWNLINK: BTS -> MS)
    R_coverage_downlink = calculate_cell_radius(P_tx_BTS_dBm, P_sens_MS_dBm, 
                                                Pathloss_exp, d0_km, G_ant_dB)
    
    # 2. Rayon maximal basé sur la couverture (UPLINK: MS -> BTS)
    R_coverage_uplink = calculate_cell_radius(P_tx_MS_dBm, P_sens_BTS_dBm, 
                                              Pathloss_exp, d0_km, G_ant_dB)
    
    # Le rayon de couverture est limité par le lien le plus faible
    Rmax_coverage = min(R_coverage_downlink, R_coverage_uplink)
    
    # 3. Rayon maximal basé sur la capacité
    # Capacité disponible: carriers_cell canaux
    # Capacité nécessaire: density_ab * activity_rate * Area
    # Area = (3*sqrt(3)/2) * R²
    # On cherche R tel que: density_ab * activity_rate * (3*sqrt(3)/2) * R² <= carriers_cell
    
    if density_ab > 0 and activity_rate > 0:
        # R² <= carriers_cell / (density_ab * activity_rate * 3*sqrt(3)/2)
        R_squared = carriers_cell / (density_ab * activity_rate * (3 * np.sqrt(3) / 2))
        Rmax_capacity = np.sqrt(R_squared)
    else:
        Rmax_capacity = float('inf')  # Pas de contrainte de capacité
    
    # 4. Rayon final = minimum des deux contraintes
    R_final = min(Rmax_coverage, Rmax_capacity)
    
    return Rmax_coverage, Rmax_capacity, R_final

def adjust_radius_for_SIR(P_BTS_dBm, P_MS_dBm, P_sens_dBm, N, SIR_min_dB, 
                          pathloss_exp, d0_km=1):
    """
    Ajuste le rayon de cellule pour respecter le critère S/I minimum
    (VERSION ORIGINALE - conservée pour compatibilité)
    
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