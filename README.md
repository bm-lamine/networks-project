# Planification d'un Réseau Cellulaire GSM

Application Python pour la planification automatique des ressources radio d'un réseau cellulaire mobile.

## 📋 Table des Matières

- [Installation](#installation)
- [Structure du Projet](#structure-du-projet)
- [Utilisation](#utilisation)
- [Exemples](#exemples)
- [Paramètres](#paramètres)
- [Résultats](#résultats)

## 🚀 Installation

### Prérequis

```bash
pip install numpy matplotlib
```

### Téléchargement

```bash
# Cloner ou télécharger les fichiers suivants:
# - back_end.py
# - front_end.py
# - params.json (optionnel)
# - demo.py (optionnel)
```

## 📁 Structure du Projet

```
tp_reseau_cellulaire/
│
├── back_end.py          # Fonctions de calcul
├── front_end.py         # Visualisation et interface
├── params.json          # Paramètres d'entrée
├── demo.py              # Script de démonstration
└── README.md            # Ce fichier
```

## 💻 Utilisation

### Option 1 : Mode Interactif

```python
python front_end.py
```

Le programme vous guidera à travers un menu interactif :

1. Charger paramètres depuis JSON
2. Utiliser paramètres par défaut
3. Éditer paramètres manuellement
4. Quitter

### Option 2 : Script Direct

```python
import back_end as be
import front_end as fe

# Charger les paramètres
params = be.load_params('params.json')

# Analyse
results = be.run_complete_analysis(params)
be.print_results(results, params)

# Visualisation
centers = fe.create_hexagon_grid(results['R_km'], grid_size=7)
freq_groups = fe.assign_frequency_groups(centers, params['N'])
fe.plot_cellular_network(results['R_km'], centers, freq_groups,
                         params['N'], results)
```

### Option 3 : Démonstration Complète

```python
python demo.py
```

## 📊 Exemples

### Exemple 1 : Analyse de Base

```python
import back_end as be

# Paramètres par défaut
params = be.get_default_params()

# Analyse
results = be.run_complete_analysis(params)

# Affichage
be.print_results(results, params)
```

**Sortie:**

```
==============================================================
RÉSULTATS DE LA PLANIFICATION DU RÉSEAU CELLULAIRE
==============================================================

📡 CONFIGURATION:
   Motif cellulaire (N): 7
   Canaux disponibles: 124
   Exposant de propagation: 3.5

📏 DIMENSIONS:
   Rayon de cellule (R): 8.456 km
   Distance de réutilisation (D): 21.788 km
   Surface de cellule: 185.333 km²

📶 INTERFÉRENCES:
   S/I minimum requis: 17.0 dB
   S/I obtenu: 19.89 dB
   Statut: ✓ OK

👥 CAPACITÉ:
   Canaux par cellule: 17
   Abonnés par cellule: 3707
   Utilisateurs actifs: 370.7
   Statut capacité: ✗ SURCHARGE
==============================================================
```

### Exemple 2 : Comparaison de Motifs

```python
import front_end as fe

params = {
    "P_BTS_dBm": 43,
    "P_MS_dBm": 23,
    "P_sens_dBm": -100,
    "N_f": 124,
    "SIR_min_dB": 17,
    "Dst_ab": 20,
    "T_act": 0.10,
    "Pathloss_exp": 3.5,
    "d0_km": 1
}

# Comparer N = 3, 7, 9
comparison = fe.compare_patterns(params, N_values=[3, 7, 9])
fe.create_comparison_table(comparison)
```

### Exemple 3 : Édition et Sauvegarde

```python
import back_end as be

# Créer de nouveaux paramètres
params = {
    "P_BTS_dBm": 46,
    "P_MS_dBm": 23,
    "P_sens_dBm": -110,
    "N_f": 200,
    "f_port_MHz": 1800,
    "N": 7,
    "SIR_min_dB": 18,
    "Dst_ab": 50,
    "T_act": 0.08,
    "Pathloss_exp": 4.0,
    "d0_km": 1
}

# Sauvegarder
be.save_params(params, 'mes_params.json')

# Recharger
params_loaded = be.load_params('mes_params.json')
```

## ⚙️ Paramètres

### Puissances

- **P_BTS_dBm** : Puissance d'émission BTS (typique: 43-46 dBm)
- **P_MS_dBm** : Puissance d'émission mobile (typique: 23-33 dBm)
- **P_sens_dBm** : Sensibilité du récepteur (typique: -100 à -110 dBm)

### Radio

- **N_f** : Nombre total de canaux (GSM-900: 124, GSM-1800: 374)
- **f_port_MHz** : Fréquence porteuse (900 ou 1800 MHz)

### Motif Cellulaire

- **N** : Taille du motif (3, 4, 7, 9, 12...)
  - Plus N est grand → meilleur S/I mais moins de canaux/cellule

### Interférences

- **SIR_min_dB** : S/I minimum requis
  - GSM: 17-18 dB
  - LTE: 12-15 dB

### Trafic

- **Dst_ab** : Densité d'abonnés (ab/km²)
  - Urbain: 50-200
  - Suburbain: 10-50
  - Rural: 1-10
- **T_act** : Taux d'activité (0.05-0.10)

### Propagation

- **Pathloss_exp** : Exposant de perte
  - Urbain: 4.0
  - Suburbain: 3.5
  - Rural: 3.0
- **d0_km** : Distance de référence (typique: 1 km)

## 📈 Résultats

L'application calcule et affiche :

### Dimensions

- **R** : Rayon de cellule (km)
- **D** : Distance de réutilisation (km)
- **Surface** : Surface de cellule (km²)

### Performance

- **S/I** : Rapport Signal/Interférence (dB)
- **Validation** : S/I obtenu ≥ S/I minimum ?

### Capacité

- **Canaux/cellule** : N_f / N
- **Abonnés/cellule** : Densité × Surface
- **Utilisateurs actifs** : Abonnés × Taux d'activité
- **Validation** : Actifs ≤ Canaux ?

### Visualisation

- Plan hexagonal coloré par groupe de fréquences
- Positions des BTS
- Légende et informations clés
- Export PNG haute résolution

## 🔍 Validation

### Critère S/I

✅ **VALIDÉ** si S/I obtenu ≥ S/I minimum

❌ **NON VALIDÉ** → Solutions :

- Augmenter N
- Réduire R (plus de cellules)
- Augmenter puissance d'émission

### Critère Capacité

✅ **OK** si Utilisateurs actifs ≤ Canaux disponibles

❌ **SURCHARGE** → Solutions :

- Réduire N (plus de canaux/cellule)
- Réduire R (moins d'abonnés/cellule)
- Augmenter taux de réutilisation

## 🎨 Visualisations Générées

Le programme génère des figures PNG :

- `cellular_network.png` : Plan cellulaire principal
- `demo_basic_N7.png` : Configuration de base
- `demo_comparison_N3.png` : Motif N=3
- `demo_comparison_N7.png` : Motif N=7

## 📝 Notes Importantes

### Hypothèses Simplificatrices

- Gains d'antennes : 2 dB (fixe)
- Seulement le premier anneau d'interféreurs (6 cellules)
- Cellules hexagonales parfaites
- Pas de relief ni d'obstacles

### Limitations

- Modèle de propagation simplifié
- Pas de prise en compte de l'ombrage (shadowing)
- Pas d'évanouissement (fading)

## 🐛 Dépannage

### Erreur : "FileNotFoundError"

→ Créer un fichier `params.json` ou utiliser les paramètres par défaut

### Erreur : "No module named 'matplotlib'"

→ Installer : `pip install matplotlib`

### S/I insuffisant

→ Augmenter N ou réduire la puissance pour diminuer R

### Surcharge de capacité

→ Réduire N ou diminuer la densité d'abonnés

## 📚 Références

- **Modèle log-distance** : PL(d) = PL(d₀) + 10n·log₁₀(d/d₀)
- **Distance de réutilisation** : D = R·√(3N)
- **S/I hexagonal** : S/I = (D/R)ⁿ / 6

## 👥 Auteurs

Master 1 – STIC  
Travail Pratique N°3  
Chargé de matière : Brahimi Said

## 📄 Licence

Projet académique - Master STIC
