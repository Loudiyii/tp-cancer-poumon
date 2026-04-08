"""
Partie 2 - Modele 2 : CNN sur radios thoraciques + fusion multimodale
Deux versions :
  v1 : image seule
  v2 : multimodal (image + probas du Modele 1)
Cible binaire : cancer_image (0/1)
"""
import os

# TF doit etre importe EN PREMIER sur Windows pour eviter les conflits DLL
import tensorflow as tf
tf.get_logger().setLevel("ERROR")
from tensorflow.keras import layers, Model, Input
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

import json
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix,
    classification_report, roc_auc_score
)

sns.set_style("whitegrid")
os.makedirs("model", exist_ok=True)
os.makedirs("figures", exist_ok=True)

RANDOM_STATE = 42
IMG_SIZE = 160
BATCH = 16
EPOCHS_HEAD = 20
EPOCHS_FINE = 30

np.random.seed(RANDOM_STATE)
tf.random.set_seed(RANDOM_STATE)

print("=" * 60)
print("PARTIE 2 - CNN + FUSION MULTIMODALE (v2 fine-tune)")
print("=" * 60)

df = pd.read_csv("data/patients_cancer_poumon.csv")
print(f"Patients : {len(df)}")

tabular_model = joblib.load("model/tabular_model.pkl")
FEATURES_TAB = [
    "age", "sexe_masculin", "presence_nodule", "subtilite_nodule",
    "taille_nodule_px", "x_nodule_norm", "y_nodule_norm",
    "tabagisme_paquets_annee", "toux_chronique", "dyspnee",
    "douleur_thoracique", "perte_poids", "spo2", "antecedent_familial",
]

def load_image(path, size=IMG_SIZE):
    img = Image.open(path).convert("RGB").resize((size, size))
    return np.array(img, dtype=np.float32)

print("\nChargement des images...")
image_paths = ["data/" + p for p in df["image_path"].values]
X_img = np.array([load_image(p) for p in image_paths])
X_img = preprocess_input(X_img)
print(f"X_img shape: {X_img.shape}")

y_bin = df["cancer_image"].values.astype(np.int32)
print(f"Cible cancer_image : {np.bincount(y_bin)}")

X_tab_raw = df[FEATURES_TAB].values
tab_probas = tabular_model.predict_proba(X_tab_raw).astype(np.float32)
print(f"Probas tabulaires shape : {tab_probas.shape}")

# Split
idx = np.arange(len(df))
idx_train, idx_test = train_test_split(
    idx, test_size=0.2, random_state=RANDOM_STATE, stratify=y_bin
)
X_img_train, X_img_test = X_img[idx_train], X_img[idx_test]
X_tab_train, X_tab_test = tab_probas[idx_train], tab_probas[idx_test]
y_train, y_test = y_bin[idx_train], y_bin[idx_test]
print(f"Train: {len(idx_train)} | Test: {len(idx_test)}")

# Class weights
class_weights = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_train)
class_weight_dict = {0: float(class_weights[0]), 1: float(class_weights[1])}
print(f"Class weights : {class_weight_dict}")

# Data augmentation plus agressive
data_aug = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.2),
    layers.RandomTranslation(0.1, 0.1),
], name="data_aug")


# ============================================
# MODELE 1 : IMAGE SEULE (avec fine-tuning)
# ============================================
def build_image_model():
    base = MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3),
                       include_top=False, weights="imagenet")
    base.trainable = False

    inp = Input(shape=(IMG_SIZE, IMG_SIZE, 3), name="image")
    x = data_aug(inp)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    out = layers.Dense(1, activation="sigmoid", name="output")(x)

    model = Model(inp, out, name="image_only")
    return model, base


print("\n" + "=" * 60)
print("MODELE 1 : CNN IMAGE SEULE")
print("=" * 60)
model_v1, base_v1 = build_image_model()
print(f"Params totaux : {model_v1.count_params():,}")

# Phase 1 : entrainement head
model_v1.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                 loss="binary_crossentropy", metrics=["accuracy"])

print("\n[Phase 1] Entrainement de la tete (base gelee)")
history_v1_head = model_v1.fit(
    X_img_train, y_train,
    validation_data=(X_img_test, y_test),
    batch_size=BATCH, epochs=EPOCHS_HEAD,
    class_weight=class_weight_dict,
    verbose=2,
)

# Phase 2 : fine-tuning (deblocage des dernieres couches)
print("\n[Phase 2] Fine-tuning (derniers blocs MobileNetV2 deblock)")
base_v1.trainable = True
for layer in base_v1.layers[:-30]:
    layer.trainable = False

model_v1.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
                 loss="binary_crossentropy", metrics=["accuracy"])

callbacks_v1 = [
    tf.keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True, monitor="val_loss"),
    tf.keras.callbacks.ReduceLROnPlateau(patience=4, factor=0.5, monitor="val_loss", min_lr=1e-7),
]

history_v1_fine = model_v1.fit(
    X_img_train, y_train,
    validation_data=(X_img_test, y_test),
    batch_size=BATCH, epochs=EPOCHS_FINE,
    class_weight=class_weight_dict,
    callbacks=callbacks_v1,
    verbose=2,
)

# Concatener les historiques
history_v1 = {
    "loss": history_v1_head.history["loss"] + history_v1_fine.history["loss"],
    "val_loss": history_v1_head.history["val_loss"] + history_v1_fine.history["val_loss"],
    "accuracy": history_v1_head.history["accuracy"] + history_v1_fine.history["accuracy"],
    "val_accuracy": history_v1_head.history["val_accuracy"] + history_v1_fine.history["val_accuracy"],
}


# ============================================
# MODELE 2 : MULTIMODAL
# ============================================
def build_multimodal_model():
    base = MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3),
                       include_top=False, weights="imagenet")
    base.trainable = False

    inp_img = Input(shape=(IMG_SIZE, IMG_SIZE, 3), name="image")
    xi = data_aug(inp_img)
    xi = base(xi, training=False)
    xi = layers.GlobalAveragePooling2D()(xi)
    xi = layers.BatchNormalization()(xi)
    xi = layers.Dropout(0.4)(xi)
    xi = layers.Dense(128, activation="relu")(xi)

    inp_tab = Input(shape=(3,), name="tab_proba")
    xt = layers.Dense(32, activation="relu")(inp_tab)
    xt = layers.Dense(16, activation="relu")(xt)

    x = layers.Concatenate()([xi, xt])
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(64, activation="relu")(x)
    out = layers.Dense(1, activation="sigmoid", name="output")(x)

    model = Model([inp_img, inp_tab], out, name="multimodal")
    return model, base


print("\n" + "=" * 60)
print("MODELE 2 : CNN MULTIMODAL (IMAGE + PROBAS TAB)")
print("=" * 60)
model_v2, base_v2 = build_multimodal_model()
print(f"Params totaux : {model_v2.count_params():,}")

model_v2.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                 loss="binary_crossentropy", metrics=["accuracy"])

print("\n[Phase 1] Entrainement de la tete")
history_v2_head = model_v2.fit(
    [X_img_train, X_tab_train], y_train,
    validation_data=([X_img_test, X_tab_test], y_test),
    batch_size=BATCH, epochs=EPOCHS_HEAD,
    class_weight=class_weight_dict,
    verbose=2,
)

print("\n[Phase 2] Fine-tuning")
base_v2.trainable = True
for layer in base_v2.layers[:-30]:
    layer.trainable = False

model_v2.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
                 loss="binary_crossentropy", metrics=["accuracy"])

callbacks_v2 = [
    tf.keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True, monitor="val_loss"),
    tf.keras.callbacks.ReduceLROnPlateau(patience=4, factor=0.5, monitor="val_loss", min_lr=1e-7),
]

history_v2_fine = model_v2.fit(
    [X_img_train, X_tab_train], y_train,
    validation_data=([X_img_test, X_tab_test], y_test),
    batch_size=BATCH, epochs=EPOCHS_FINE,
    class_weight=class_weight_dict,
    callbacks=callbacks_v2,
    verbose=2,
)

history_v2 = {
    "loss": history_v2_head.history["loss"] + history_v2_fine.history["loss"],
    "val_loss": history_v2_head.history["val_loss"] + history_v2_fine.history["val_loss"],
    "accuracy": history_v2_head.history["accuracy"] + history_v2_fine.history["accuracy"],
    "val_accuracy": history_v2_head.history["val_accuracy"] + history_v2_fine.history["val_accuracy"],
}


# ============================================
# EVALUATION
# ============================================
def eval_model(model, X, y, name):
    y_proba = model.predict(X, verbose=0).ravel()
    y_pred = (y_proba > 0.5).astype(int)
    acc = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    try:
        auc = roc_auc_score(y, y_proba)
    except ValueError:
        auc = np.nan
    print(f"\n[{name}]")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  F1       : {f1:.4f}")
    print(f"  ROC-AUC  : {auc:.4f}")
    print(classification_report(y, y_pred, target_names=["Non probable", "Probable"]))
    return {"accuracy": float(acc), "f1": float(f1), "roc_auc": float(auc),
            "y_pred": y_pred, "y_proba": y_proba}

print("\n" + "=" * 60)
print("EVALUATION FINALE SUR TEST SET")
print("=" * 60)
res_v1 = eval_model(model_v1, X_img_test, y_test, "IMAGE SEULE")
res_v2 = eval_model(model_v2, [X_img_test, X_tab_test], y_test, "MULTIMODAL")


# ============================================
# FIGURES
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
for ax, hist, title in zip(axes[0], [history_v1, history_v2], ["Image seule", "Multimodal"]):
    ax.plot(hist["loss"], label="Train loss", color="#3498db")
    ax.plot(hist["val_loss"], label="Val loss", color="#e74c3c")
    ax.axvline(x=EPOCHS_HEAD, color="gray", linestyle="--", alpha=0.5, label="Fine-tune")
    ax.set_title(f"Loss - {title}", fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()

for ax, hist, title in zip(axes[1], [history_v1, history_v2], ["Image seule", "Multimodal"]):
    ax.plot(hist["accuracy"], label="Train acc", color="#2ecc71")
    ax.plot(hist["val_accuracy"], label="Val acc", color="#f39c12")
    ax.axvline(x=EPOCHS_HEAD, color="gray", linestyle="--", alpha=0.5, label="Fine-tune")
    ax.set_title(f"Accuracy - {title}", fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.legend()
    ax.set_ylim(0, 1.05)

plt.tight_layout()
plt.savefig("figures/08_courbes_apprentissage.png", bbox_inches="tight", dpi=150)
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, res, title in zip(axes, [res_v1, res_v2], ["Image seule", "Multimodal"]):
    cm = confusion_matrix(y_test, res["y_pred"])
    sns.heatmap(cm, annot=True, fmt="d", cmap="Purples",
                xticklabels=["Non", "Oui"], yticklabels=["Non", "Oui"], ax=ax)
    ax.set_xlabel("Prediction")
    ax.set_ylabel("Reel")
    ax.set_title(f"Confusion - {title}", fontweight="bold")
plt.tight_layout()
plt.savefig("figures/09_confusion_cnn.png", bbox_inches="tight", dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(10, 6))
metrics_names = ["Accuracy", "F1", "ROC-AUC"]
v1_scores = [res_v1["accuracy"], res_v1["f1"], res_v1["roc_auc"]]
v2_scores = [res_v2["accuracy"], res_v2["f1"], res_v2["roc_auc"]]
x = np.arange(len(metrics_names))
width = 0.35
ax.bar(x - width / 2, v1_scores, width, label="Image seule",
       color="#3498db", edgecolor="black")
ax.bar(x + width / 2, v2_scores, width, label="Multimodal",
       color="#e74c3c", edgecolor="black")
ax.set_xticks(x)
ax.set_xticklabels(metrics_names)
ax.set_ylabel("Score")
ax.set_title("Image seule vs Multimodal (image + probas tabulaires)",
             fontweight="bold")
ax.legend()
ax.set_ylim(0, 1.15)
for i, (a, b) in enumerate(zip(v1_scores, v2_scores)):
    ax.text(i - width / 2, a + 0.02, f"{a:.3f}", ha="center", fontsize=9)
    ax.text(i + width / 2, b + 0.02, f"{b:.3f}", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig("figures/10_comparaison_cnn.png", bbox_inches="tight", dpi=150)
plt.close()


# ============================================
# SAUVEGARDE
# ============================================
model_v1.save("model/cnn_image_only.keras")
model_v2.save("model/cnn_multimodal.keras")

metadata_cnn = {
    "img_size": IMG_SIZE,
    "batch_size": BATCH,
    "epochs_head": EPOCHS_HEAD,
    "epochs_fine": EPOCHS_FINE,
    "image_only": {k: v for k, v in res_v1.items() if k not in ["y_pred", "y_proba"]},
    "multimodal": {k: v for k, v in res_v2.items() if k not in ["y_pred", "y_proba"]},
    "backbone": "MobileNetV2 (ImageNet, fine-tuned last 30 layers)",
    "target": "cancer_image (binaire)",
    "class_weights": class_weight_dict,
}
with open("model/cnn_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata_cnn, f, indent=2, ensure_ascii=False)

print("\nModeles sauvegardes : model/cnn_image_only.keras + model/cnn_multimodal.keras")
