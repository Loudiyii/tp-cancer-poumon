# Partie 3 — Analyse et interprétation

## 1. Le modèle multimodal est-il meilleur que le modèle image seule ?

**Oui, de manière spectaculaire :**

| Modèle | Accuracy | F1-score | ROC-AUC |
|--------|----------|----------|---------|
| CNN image seule | ~51% | ~0.40 | ~0.55 |
| CNN multimodal (image + probas tabulaires) | **100%** | **1.00** | **1.00** |

Le modèle image seule se comporte à peine mieux qu'un choix aléatoire (50%), tandis que le modèle multimodal atteint un score parfait sur le jeu de test. Cette différence massive démontre que **les données tabulaires apportent quasiment toute l'information discriminante** dans ce dataset.

## 2. En quoi les données tabulaires améliorent-elles (ou non) la décision finale ?

Les données tabulaires transforment une tâche de vision quasiment impossible (184 images seulement, dont 147 pour l'entraînement, avec des classes visuellement subtiles) en une tâche triviale. Plus précisément :

- **Branche tabulaire** : le modèle 1 (LogisticRegression) atteint déjà **100% sur les 3 classes de risque** grâce à des corrélations déterministes entre les variables cliniques et l'étiquette (voir section "Limites").
- **Branche image** : ne dispose que de 147 radios pour apprendre, ce qui est largement insuffisant pour un CNN même avec transfer learning (MobileNetV2) et fine-tuning.
- **Fusion** : le réseau concatène les features image (128 dim) aux 3 probabilités tabulaires, puis les fait passer dans une couche dense. En pratique, il apprend essentiellement à **ignorer les features image** et à s'appuyer sur les probas tabulaires qui sont déjà parfaitement séparables.

Dans un contexte réel où les variables cliniques seraient bruitées, l'image apporterait probablement une vraie valeur ajoutée complémentaire — mais ici, elle est fonctionnellement redondante.

## 3. Limites du jeu de données utilisé

Plusieurs limites majeures ont été identifiées :

### 3.1 Taille du dataset
- **184 patients / 184 images** : extrêmement petit pour du deep learning médical. Les benchmarks standards (ChestX-ray14, CheXpert) contiennent >100 000 radios.
- **Split 80/20** → 37 exemples en test seulement. Les métriques sur un si petit ensemble ont une **très grande variance** (un seul faux positif change l'accuracy de 2.7 points).

### 3.2 Données synthétiques / déterministes
Le dataset tabulaire présente des corrélations artificielles parfaites :
- **SpO₂** = 92% pour **tous** les malins, 95% pour tous les bénins
- **Tous les symptômes** (toux, dyspnée, douleur, perte de poids) sont à 1 pour les malins et 0 pour les bénins
- Résultat : les 3 algorithmes testés (LogisticRegression, RandomForest, GradientBoosting) atteignent **tous 100% d'accuracy**, ce qui est un indicateur fort d'un dataset non réaliste.

Dans un contexte clinique réel :
- Un patient bénin peut avoir SpO₂ = 91% (asthme non lié au cancer)
- Un patient sain peut tousser
- Des antécédents familiaux n'impliquent pas de cancer
- Le bruit et les corrélations partielles rendent la tâche beaucoup plus difficile

### 3.3 Déséquilibre des classes
- **Sain** : 30 (16%) · **Bénin** : 54 (29%) · **Malin** : 100 (54%)
- Classe "sain" sous-représentée → risque de sur-détection dans un contexte réel.

### 3.4 Qualité et homogénéité des images JSRT
Les radios JSRT sont :
- Anciennes (acquisitions argentiques numérisées)
- Toutes du **même institut japonais** (biais géographique/démographique)
- Haut contraste et centrage homogène (peu représentatif des variations terrain)

### 3.5 Absence de validation externe
Aucun jeu de test indépendant (autre hôpital, autre machine). Le 100% obtenu par le modèle tabulaire ne garantit **aucune généralisation** à un nouveau contexte.

## 4. Améliorations proposées pour un contexte médical réel

### 4.1 Données

1. **Augmenter le dataset** : viser **≥ 10 000 patients** via collecte multi-centres (plusieurs hôpitaux, plusieurs pays, plusieurs machines)
2. **Introduire du bruit réaliste** dans les variables cliniques : distributions gaussiennes autour des valeurs moyennes, corrélations partielles
3. **Ajouter des données manquantes** (missing at random) puisque c'est la norme en clinique
4. **Validation externe** : garder un centre entier pour le test, pas seulement un split aléatoire

### 4.2 Modèle tabulaire

1. **Gradient boosting avancé** (XGBoost, LightGBM, CatBoost) + tuning des hyperparamètres via Optuna
2. **Calibration des probabilités** (Platt scaling, isotonic regression) pour que le score soit interprétable comme une probabilité réelle
3. **Feature importance** (SHAP values) pour justifier chaque prédiction au clinicien
4. **Incertitude** : ajouter une estimation de la confiance (Bayesian NN, Monte Carlo dropout, Conformal prediction)

### 4.3 Modèle image

1. **Transfer learning à partir de modèles médicaux** pré-entraînés : CheXNet, TorchXRayVision, plutôt que MobileNetV2 (ImageNet)
2. **Segmentation préliminaire** du nodule via un U-Net, puis classification sur le crop
3. **Augmentation spécifique** : elastic deformation, histogram equalization, CLAHE
4. **Attention visuelle** (Grad-CAM, attention maps) pour montrer quelle zone a influencé la prédiction → crucial pour l'acceptation clinique

### 4.4 Fusion multimodale

1. **Cross-attention** entre features image et embeddings tabulaires (au lieu de simple concaténation)
2. **Pondération apprise** : laisser le modèle décider à quel point il fait confiance à chaque modalité selon le contexte
3. **Robustesse aux modalités manquantes** : entraîner avec du dropout sur une modalité entière (parfois image seule, parfois tabulaire seule) pour que le modèle reste performant quand une donnée manque

### 4.5 MLOps et déploiement

1. **Monitoring continu** : drift detection sur les données d'entrée et les distributions de prédictions
2. **Versioning strict** des modèles et des datasets (DVC, MLflow, Weights & Biases)
3. **A/B testing** en conditions réelles avant déploiement final
4. **Audit logs** pour traçabilité (chaque prédiction associée au modèle version X avec les inputs)
5. **Explications obligatoires** : aucune prédiction sans justification visuelle + tabulaire
6. **Cadre réglementaire** : conformité CE médical, RGPD, ISO 13485, validation clinique

### 4.6 Sécurité et éthique

1. **Biais d'équité** : vérifier que les performances sont comparables par âge, sexe, origine ethnique
2. **Faux négatifs = priorité absolue** : mieux vaut un faux positif (examen complémentaire) qu'un faux négatif (cancer manqué) → seuil de décision ajusté en conséquence
3. **Human in the loop** : le modèle ne remplace jamais le radiologue, il est un outil d'aide à la décision avec score de confiance
4. **Consentement et anonymisation** des données patient

## 5. Conclusion

Ce TP démontre un pipeline MLOps complet — de l'EDA au déploiement cloud — mais révèle surtout que **la qualité des données prime sur la complexité du modèle**. Notre modèle multimodal atteint 100% non pas grâce à la fusion, mais parce que les variables cliniques synthétiques sont déjà parfaitement séparables. L'image ne contribue presque pas à la décision.

**En conditions réelles**, les résultats seraient très différents :
- Le modèle tabulaire chuterait probablement à 75-85% avec des données bruitées
- Le CNN image, entraîné sur 10 000+ radios, atteindrait probablement 85-92%
- La fusion multimodale apporterait un gain marginal mais réel (2-5 points)

Le plus grand apport de ce TP n'est donc pas le modèle lui-même, mais l'**architecture MLOps** qui permet d'itérer rapidement sur les modèles (entraînement → API → frontend → déploiement → monitoring) — un cycle court qui est la vraie compétence industrielle.
