# PulmoAI — Détection du cancer pulmonaire par fusion multimodale

TP noté MLOps — M2 ESIC IA/ML/DL · 2025-2026
Professeur : Redouane FENZI

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌────────────────┐
│  Next.js front  │ ───► │  FastAPI backend │ ───► │  ML/DL Models  │
│  Tailwind+shadcn│      │  /api/predict-*  │      │  sklearn + TF  │
└─────────────────┘      └──────────────────┘      └────────────────┘
      Vercel                    Render                  Docker
```

## Stack

| Composant | Technologie |
|-----------|-------------|
| Frontend  | Next.js 16 + TypeScript + Tailwind CSS + shadcn/ui |
| Backend   | FastAPI + Uvicorn |
| Modèle 1 (tabulaire) | scikit-learn (LogisticRegression, RandomForest, GradientBoosting) |
| Modèle 2 (image) | TensorFlow/Keras + MobileNetV2 (fine-tuned) |
| Fusion    | Concaténation features image + probabilités tabulaires |
| Conteneurisation | Docker |
| Déploiement | Render (backend) + Vercel (frontend) |

## Les 5 parties du TP

### Partie 0 — Analyse exploratoire (2 pts)
→ `src/eda.py` · figures dans `figures/`

### Partie 1 — Modèle tabulaire 3 classes (5 pts)
→ `src/train_tabular.py` · modèle sauvegardé dans `model/tabular_model.pkl`

### Partie 2 — CNN image + multimodal (6 pts)
→ `src/train_image.py` · modèles `model/cnn_image_only.keras` et `model/cnn_multimodal.keras`

### Partie 3 — Analyse & interprétation (3 pts)
→ voir rapport PDF

### Partie 4 — MLOps : IHM + déploiement (4 pts)
→ backend FastAPI (`backend/`) + frontend Next.js (`frontend/`) + Docker

## Exécution locale

### 1. Entraîner les modèles

```bash
python src/eda.py
python src/train_tabular.py
python src/train_image.py
```

### 2. Lancer le backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Documentation Swagger : http://localhost:8000/docs

### 3. Lancer le frontend

```bash
cd frontend
npm install
npm run dev
```

Application : http://localhost:3000

### 4. Docker (backend)

```bash
docker build -t pulmoai .
docker run -p 8000:8000 pulmoai
```

## Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | Vérification du service + métriques des modèles |
| POST | `/api/predict-tabular` | Prédiction du risque tabulaire (3 classes) |
| POST | `/api/predict-cancer` | Prédiction cancer multimodale (image + patient) |

## Dataset

- **184 patients** avec 14 variables cliniques
- **184 radios thoraciques** (JSRT) : 30 sain · 54 bénin · 100 malin
- Cibles :
  - `risque_malignite` ∈ {0, 1, 2}
  - `cancer_image` ∈ {0, 1}
