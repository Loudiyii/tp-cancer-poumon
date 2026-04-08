"""
Partie 0 - Analyse Exploratoire des Données (EDA)
Génère les statistiques descriptives et les visualisations.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 150
plt.rcParams["font.family"] = "DejaVu Sans"

OUT_DIR = "figures"
os.makedirs(OUT_DIR, exist_ok=True)

# Chargement
df = pd.read_csv("data/patients_cancer_poumon.csv")
print(f"Shape: {df.shape}")
print(f"Colonnes: {list(df.columns)}")

# Stats de base
with open(f"{OUT_DIR}/stats.txt", "w", encoding="utf-8") as f:
    f.write("=== STATISTIQUES DESCRIPTIVES ===\n\n")
    f.write(f"Nombre de patients : {len(df)}\n")
    f.write(f"Nombre de variables : {df.shape[1]}\n\n")
    f.write("=== VALEURS MANQUANTES ===\n")
    f.write(str(df.isnull().sum()) + "\n\n")
    f.write("=== STATS NUMERIQUES ===\n")
    f.write(str(df.describe()) + "\n\n")
    f.write("=== DISTRIBUTION RISQUE MALIGNITE ===\n")
    f.write(str(df["risque_malignite"].value_counts().sort_index()) + "\n\n")
    f.write("=== DISTRIBUTION CANCER IMAGE ===\n")
    f.write(str(df["cancer_image"].value_counts().sort_index()) + "\n")

print("Stats sauvegardees")

# ==== Visualisation 1 : Distribution des classes ====
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

labels_risque = {0: "0 - Faible", 1: "1 - Intermediaire", 2: "2 - Eleve"}
risque_counts = df["risque_malignite"].value_counts().sort_index()
colors_risque = ["#2ecc71", "#f39c12", "#e74c3c"]
axes[0].bar([labels_risque[i] for i in risque_counts.index], risque_counts.values,
            color=colors_risque, edgecolor="black")
axes[0].set_title("Distribution du risque de malignite (Modele 1)", fontsize=12, fontweight="bold")
axes[0].set_ylabel("Nombre de patients")
for i, v in enumerate(risque_counts.values):
    axes[0].text(i, v + 1, str(v), ha="center", fontweight="bold")

cancer_counts = df["cancer_image"].value_counts().sort_index()
axes[1].bar(["0 - Non probable", "1 - Probable"], cancer_counts.values,
            color=["#3498db", "#c0392b"], edgecolor="black")
axes[1].set_title("Distribution du cancer image (Modele 2)", fontsize=12, fontweight="bold")
axes[1].set_ylabel("Nombre de patients")
for i, v in enumerate(cancer_counts.values):
    axes[1].text(i, v + 1, str(v), ha="center", fontweight="bold")

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/01_distribution_classes.png", bbox_inches="tight")
plt.close()
print("Figure 1 : distribution classes")

# ==== Visualisation 2 : Age + SpO2 par risque ====
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

for risque, color in zip([0, 1, 2], colors_risque):
    data = df[df["risque_malignite"] == risque]["age"]
    axes[0].hist(data, bins=15, alpha=0.6, label=labels_risque[risque],
                 color=color, edgecolor="black")
axes[0].set_title("Age par niveau de risque de malignite", fontweight="bold")
axes[0].set_xlabel("Age (annees)")
axes[0].set_ylabel("Frequence")
axes[0].legend()

df_plot = df.copy()
df_plot["Risque"] = df_plot["risque_malignite"].map(labels_risque)
sns.boxplot(data=df_plot, x="Risque", y="spo2", ax=axes[1],
            palette=colors_risque, order=[labels_risque[i] for i in [0, 1, 2]])
axes[1].set_title("Saturation O2 (SpO2) par niveau de risque", fontweight="bold")
axes[1].set_xlabel("Risque de malignite")
axes[1].set_ylabel("SpO2 (%)")

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/02_age_spo2.png", bbox_inches="tight")
plt.close()
print("Figure 2 : age/spo2")

# ==== Visualisation 3 : Matrice de correlation ====
num_cols = ["age", "sexe_masculin", "presence_nodule", "subtilite_nodule",
            "taille_nodule_px", "tabagisme_paquets_annee", "toux_chronique",
            "dyspnee", "douleur_thoracique", "perte_poids", "spo2",
            "antecedent_familial", "risque_malignite", "cancer_image"]
corr = df[num_cols].corr()

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
ax.set_title("Matrice de correlation des variables", fontweight="bold", fontsize=13)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/03_correlation.png", bbox_inches="tight")
plt.close()
print("Figure 3 : correlation")

# ==== Visualisation 4 : Tabagisme vs risque ====
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

sns.boxplot(data=df_plot, x="Risque", y="tabagisme_paquets_annee",
            palette=colors_risque, ax=axes[0],
            order=[labels_risque[i] for i in [0, 1, 2]])
axes[0].set_title("Tabagisme (paquets-annee) par risque", fontweight="bold")
axes[0].set_xlabel("Risque de malignite")
axes[0].set_ylabel("Paquets-annee")

sns.boxplot(data=df_plot, x="Risque", y="taille_nodule_px",
            palette=colors_risque, ax=axes[1],
            order=[labels_risque[i] for i in [0, 1, 2]])
axes[1].set_title("Taille du nodule (pixels) par risque", fontweight="bold")
axes[1].set_xlabel("Risque de malignite")
axes[1].set_ylabel("Taille (px)")

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/04_tabagisme_nodule.png", bbox_inches="tight")
plt.close()
print("Figure 4 : tabagisme/nodule")

# ==== Visualisation 5 : Radios representatives ====
classes = ["sain", "benin", "malin"]
class_labels = {"sain": "Sain", "benin": "Benin", "malin": "Malin"}

fig, axes = plt.subplots(3, 3, figsize=(11, 11))
for i, cls in enumerate(classes):
    cls_dir = f"data/jsrt_subset/{cls}"
    files = sorted(os.listdir(cls_dir))[:3]
    for j, fname in enumerate(files):
        img = Image.open(os.path.join(cls_dir, fname))
        axes[i, j].imshow(img, cmap="gray")
        axes[i, j].set_title(f"{class_labels[cls]} - {fname}", fontsize=10)
        axes[i, j].axis("off")

plt.suptitle("Radios thoraciques representatives par classe",
             fontsize=14, fontweight="bold", y=1.00)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/05_radios_representatives.png", bbox_inches="tight")
plt.close()
print("Figure 5 : radios representatives")

print("\nEDA terminee. Figures sauvegardees dans figures/")
