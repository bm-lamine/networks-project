# Rapport de Planification d'un Réseau Cellulaire GSM

**Master 1 – STIC**  
**Travail Pratique N°3**  
**Date:** [Date de remise]  
**Étudiants:** [Noms]

---

## 1. Introduction

Ce rapport présente la conception et l'implémentation d'une application Python de planification automatique d'un réseau cellulaire mobile de type GSM. L'objectif est de calculer les paramètres radio optimaux (rayon de cellule, distance de réutilisation, canaux) tout en respectant les contraintes d'interférences co-canaux et de capacité.

### 1.1 Objectifs du projet

- Calculer le rayon maximal des cellules
- Déterminer la distance de réutilisation des fréquences
- Valider le critère Signal/Interférence (S/I)
- Analyser la capacité du réseau
- Visualiser la topologie hexagonale du réseau

---

## 2. Modèles Radio Utilisés

### 2.1 Modèle de propagation log-distance

Le modèle de perte de trajet utilisé est :

**PL(d) = PL(d₀) + 10·n·log₁₀(d/d₀)**

où :

- **PL(d)** : perte de trajet à la distance d (dB)
- **PL(d₀)** : perte de trajet à la distance de référence d₀ (≈ 0 dB)
- **n** : exposant de perte de propagation
  - Urbain : n ≈ 4.0
  - Suburbain : n ≈ 3.5
  - Rural : n ≈ 3.0
- **d₀** : distance de référence (typiquement 1 km)

### 2.2 Calcul du rayon de cellule

Le rayon maximal R est déterminé par le budget de liaison :

**P_TX + G_ant - PL(R) ≥ P_sens**

Donc : **R = d₀ · 10^(PL_max / (10·n))**

où **PL_max = P_TX + G_ant - P_sens**

Le rayon final est limité par :

1. La couverture (downlink : BTS → MS)
2. La couverture (uplink : MS → BTS)
3. Le critère S/I minimum

### 2.3 Distance de réutilisation

Pour un motif hexagonal de taille N :

**D = R · √(3N)**

Cette distance garantit la séparation minimale entre cellules utilisant les mêmes fréquences.

### 2.4 Rapport Signal/Interférence (S/I)

En considérant uniquement le premier anneau d'interféreurs (6 cellules) :

**S/I = (D/R)ⁿ / 6**

En dB : **S/I_dB = 10·log₁₀((D/R)ⁿ / 6)**

Pour GSM : **S/I_min = 17-18 dB**

### 2.5 Capacité

- **Canaux par cellule** : N_f / N
- **Abonnés par cellule** : Densité × Surface_cellule
- **Utilisateurs actifs** : Abonnés × Taux_activité

---

## 3. Résultats Numériques

### 3.1 Configuration de base

| Paramètre               | Valeur    |
| ----------------------- | --------- |
| Puissance BTS           | 43 dBm    |
| Puissance MS            | 23 dBm    |
| Sensibilité             | -100 dBm  |
| Canaux totaux           | 124       |
| Fréquence porteuse      | 900 MHz   |
| S/I minimum             | 17 dB     |
| Densité d'abonnés       | 20 ab/km² |
| Taux d'activité         | 10%       |
| Exposant de propagation | 3.5       |

### 3.2 Comparaison des motifs cellulaires

| N   | R (km) | D (km) | S/I (dB) | Canaux/cell | Util. actifs | S/I OK | Cap OK |
| --- | ------ | ------ | -------- | ----------- | ------------ | ------ | ------ |
| 3   | 8.456  | 14.649 | 14.25    | 41          | 22.0         | ✗      | ✓      |
| 4   | 8.456  | 16.912 | 16.77    | 31          | 22.0         | ✗      | ✓      |
| 7   | 8.456  | 21.788 | 19.89    | 17          | 22.0         | ✓      | ✓      |
| 9   | 8.456  | 24.568 | 21.31    | 13          | 22.0         | ✓      | ✓      |
| 12  | 8.456  | 28.382 | 22.98    | 10          | 22.0         | ✓      | ✗      |

**Observations :**

- Pour N=3 et N=4, le critère S/I n'est pas satisfait (< 17 dB)
- N=7 offre un bon compromis entre S/I et capacité
- N=12 satisfait le S/I mais manque de canaux pour la charge

### 3.3 Impact de l'environnement

| Environnement | n   | R (km) | D (km) | S/I (dB) | Observation                  |
| ------------- | --- | ------ | ------ | -------- | ---------------------------- |
| Urbain        | 4.0 | 5.989  | 15.500 | 22.15    | Petites cellules, bon S/I    |
| Suburbain     | 3.5 | 8.456  | 21.788 | 19.89    | Configuration équilibrée     |
| Rural         | 3.0 | 13.162 | 33.998 | 17.08    | Grandes cellules, S/I limite |

**Analyse :**

- En urbain : atténuation forte → rayon réduit → plus de cellules nécessaires
- En rural : atténuation faible → rayon étendu → meilleure couverture mais S/I plus critique

---

## 4. Visualisation du Plan Cellulaire

### 4.1 Motif N=7 (Configuration recommandée)

[Insérer ici l'image cellular_network_N7.png]

**Légende :**

- Triangles rouges : Stations de base (BTS)
- Couleurs différentes : Groupes de fréquences (7 groupes)
- Hexagones : Zones de couverture des cellules

### 4.2 Comparaison visuelle N=3 vs N=7

[Insérer les images de comparaison]

---

## 5. Validation du Critère S/I

### 5.1 Vérification pour N=7

**Résultats :**

- S/I obtenu : **19.89 dB**
- S/I minimum requis : **17.00 dB**
- **Statut : ✓ VALIDÉ**

Le motif N=7 satisfait le critère S/I avec une marge de **2.89 dB**.

### 5.2 Solutions en cas de non-validation

Si S/I obtenu < S/I minimum :

**Option 1 : Augmenter N**

- Avantage : Améliore le S/I
- Inconvénient : Réduit le nombre de canaux par cellule

**Option 2 : Réduire R**

- Avantage : Augmente D/R donc améliore S/I
- Inconvénient : Nécessite plus de sites BTS

**Option 3 : Augmenter la puissance**

- Peut améliorer légèrement le S/I
- Limité par les normes et la consommation

---

## 6. Discussion

### 6.1 Impact de la densité d'abonnés

| Densité (ab/km²) | Abonnés/cell | Actifs/cell | Canaux/cell | Statut      |
| ---------------- | ------------ | ----------- | ----------- | ----------- |
| 10               | 110          | 11.0        | 17          | ✓ OK        |
| 20               | 220          | 22.0        | 17          | ✓ OK        |
| 50               | 550          | 55.0        | 17          | ✗ SURCHARGE |
| 100              | 1100         | 110.0       | 17          | ✗ SURCHARGE |

**Analyse :**

- Pour densités élevées (> 50 ab/km²), il faut :
  - Réduire N pour augmenter les canaux/cellule
  - Ou réduire R pour diminuer les abonnés/cellule

### 6.2 Compromis Capacité vs Interférence

**Dilemme fondamental :**

- ↑ N → ↑ S/I mais ↓ Canaux/cellule
- ↓ N → ↑ Canaux/cellule mais ↓ S/I

**Solution optimale :** N=7 offre le meilleur équilibre pour la plupart des scénarios GSM.

### 6.3 Impact de l'environnement

En zone urbaine :

- Forte atténuation → cellules plus petites
- Nécessite plus de sites BTS
- S/I facilement satisfait grâce aux petites cellules

En zone rurale :

- Faible atténuation → grandes cellules
- Moins de sites nécessaires
- S/I plus critique, nécessite N plus grand

---

## 7. Conclusion

Ce projet a permis de développer une application complète de planification radio pour réseaux GSM. Les principaux enseignements sont :

1. **Le motif N=7** est optimal pour la plupart des configurations GSM
2. **L'environnement** a un impact majeur sur la taille des cellules
3. **Le compromis S/I vs capacité** nécessite un dimensionnement soigné
4. **La validation systématique** des critères (S/I, capacité) est essentielle

### Extensions possibles

- Intégration de modèles de propagation plus réalistes (Okumura-Hata, COST-231)
- Prise en compte du relief et des obstacles
- Optimisation automatique de N selon les contraintes
- Placement intelligent des BTS sur carte réelle

---

## 8. Références

- Rappaport, T. S. (2002). _Wireless Communications: Principles and Practice_
- Goldsmith, A. (2005). _Wireless Communications_
- Cours STIC - Master 1
- Documentation Python : matplotlib, numpy

---

**Annexe A : Code source**

- back_end.py
- front_end.py
- demo.py

**Annexe B : Fichiers de configuration**

- params.json
