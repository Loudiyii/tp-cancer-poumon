"""
Partie 1 - Modele 1 : Classification tabulaire du risque de malignite (3 classes)
Compare 3 algorithmes et sauvegarde le meilleur.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay
)

sns.set_style("whitegrid")
os.makedirs("model", exist_ok=True)
os.makedirs("figures", exist_ok=True)

RANDOM_STATE = 42

print("=" * 60)
print("PARTIE 1 - MODELE TABULAIRE (3 classes de risque)")
print("=" * 60)

df = pd.read_csv("data/patients_cancer_poumon.csv")

FEATURES = [
    "age", "sexe_masculin", "presence_nodule", "subtilite_nodule",
    "taille_nodule_px", "x_nodule_norm", "y_nodule_norm",
    "tabagisme_paquets_annee", "toux_chronique", "dyspnee",
    "douleur_thoracique", "perte_poids", "spo2", "antecedent_familial",
]
TARGET = "risque_malignite"

X = df[FEATURES].values
y = df[TARGET].values

print(f"\nFeatures : {len(FEATURES)}")
print(f"Samples  : {len(X)}")
print(f"Classes  : {np.unique(y)}  (0=faible, 1=intermediaire, 2=eleve)")
print(f"Distribution: {np.bincount(y)}")

# Split stratifie
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"\nTrain : {len(X_train)} | Test : {len(X_test)}")

# Modeles a comparer
models = {
    "LogisticRegression": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE,
                                   multi_class="multinomial")),
    ]),
    "RandomForest": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE,
                                       class_weight="balanced")),
    ]),
    "GradientBoosting": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_STATE)),
    ]),
}

# Cross-validation + evaluation
results = {}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

print("\n" + "=" * 60)
print("ENTRAINEMENT ET EVALUATION")
print("=" * 60)

for name, model in models.items():
    print(f"\n--- {name} ---")
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    f1_weighted = f1_score(y_test, y_pred, average="weighted")

    print(f"CV accuracy : {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print(f"Test accuracy : {acc:.4f}")
    print(f"Test F1 macro : {f1_macro:.4f}")
    print(f"Test F1 weighted : {f1_weighted:.4f}")
    print(classification_report(y_test, y_pred, target_names=["Faible", "Intermediaire", "Eleve"]))

    results[name] = {
        "cv_accuracy_mean": float(cv_scores.mean()),
        "cv_accuracy_std": float(cv_scores.std()),
        "test_accuracy": float(acc),
        "test_f1_macro": float(f1_macro),
        "test_f1_weighted": float(f1_weighted),
        "model": model,
    }

# Selection du meilleur
best_name = max(results, key=lambda k: results[k]["test_f1_macro"])
best_model = results[best_name]["model"]
print("\n" + "=" * 60)
print(f"MEILLEUR MODELE : {best_name}")
print(f"Accuracy : {results[best_name]['test_accuracy']:.4f}")
print(f"F1 macro : {results[best_name]['test_f1_macro']:.4f}")
print("=" * 60)

# Matrice de confusion du meilleur
y_pred_best = best_model.predict(X_test)
cm = confusion_matrix(y_test, y_pred_best)

fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Faible", "Intermediaire", "Eleve"],
            yticklabels=["Faible", "Intermediaire", "Eleve"], ax=ax)
ax.set_xlabel("Prediction")
ax.set_ylabel("Reel")
ax.set_title(f"Matrice de confusion - {best_name}", fontweight="bold")
plt.tight_layout()
plt.savefig("figures/06_confusion_tabular.png", bbox_inches="tight", dpi=150)
plt.close()

# Comparaison des modeles
fig, ax = plt.subplots(figsize=(10, 6))
names = list(results.keys())
accs = [results[n]["test_accuracy"] for n in names]
f1s = [results[n]["test_f1_macro"] for n in names]
x = np.arange(len(names))
width = 0.35
ax.bar(x - width / 2, accs, width, label="Accuracy", color="#3498db", edgecolor="black")
ax.bar(x + width / 2, f1s, width, label="F1 macro", color="#e67e22", edgecolor="black")
ax.set_xticks(x)
ax.set_xticklabels(names)
ax.set_ylabel("Score")
ax.set_title("Comparaison des modeles tabulaires", fontweight="bold")
ax.legend()
ax.set_ylim(0, 1.1)
for i, (a, f) in enumerate(zip(accs, f1s)):
    ax.text(i - width / 2, a + 0.02, f"{a:.3f}", ha="center", fontsize=9)
    ax.text(i + width / 2, f + 0.02, f"{f:.3f}", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig("figures/07_comparaison_tabular.png", bbox_inches="tight", dpi=150)
plt.close()

# Probabilites de prediction sur quelques exemples
probas = best_model.predict_proba(X_test[:5])
print("\nProbabilites de prediction (5 premiers patients du test) :")
print("  [Faible, Intermediaire, Eleve]")
for i, p in enumerate(probas):
    print(f"  Patient {i+1}: {p.round(3)} -> reel={y_test[i]}, predit={y_pred_best[i]}")

# Sauvegarde
joblib.dump(best_model, "model/tabular_model.pkl")
metadata = {
    "best_model": best_name,
    "features": FEATURES,
    "target": TARGET,
    "n_classes": 3,
    "class_names": ["Faible", "Intermediaire", "Eleve"],
    "results": {k: {kk: vv for kk, vv in v.items() if kk != "model"}
                for k, v in results.items()},
}
with open("model/tabular_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("\nModele et metadata sauvegardes dans model/")
print("tabular_model.pkl + tabular_metadata.json")
