"""
Backend FastAPI - Prediction cancer pulmonaire
Expose deux endpoints :
  POST /api/predict-tabular : Modele 1 - risque de malignite (3 classes)
  POST /api/predict-cancer  : Modele 2 multimodal (image + probas tabulaires)
"""
import os
import io
import json
import numpy as np
import joblib
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# ============================================
# Configuration
# ============================================
IMG_SIZE = 160
MODEL_DIR = os.environ.get("MODEL_DIR", "../model")

FEATURES_TAB = [
    "age", "sexe_masculin", "presence_nodule", "subtilite_nodule",
    "taille_nodule_px", "x_nodule_norm", "y_nodule_norm",
    "tabagisme_paquets_annee", "toux_chronique", "dyspnee",
    "douleur_thoracique", "perte_poids", "spo2", "antecedent_familial",
]

RISQUE_LABELS = {0: "Faible", 1: "Intermediaire", 2: "Eleve"}

# ============================================
# App
# ============================================
app = FastAPI(
    title="Cancer Pulmonaire - API",
    description="API de prediction du risque de cancer pulmonaire (tabulaire + images)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Chargement des modeles
# ============================================
print("Chargement des modeles...")
tabular_model = joblib.load(os.path.join(MODEL_DIR, "tabular_model.pkl"))
with open(os.path.join(MODEL_DIR, "tabular_metadata.json"), "r", encoding="utf-8") as f:
    tabular_metadata = json.load(f)

cnn_multimodal = tf.keras.models.load_model(os.path.join(MODEL_DIR, "cnn_multimodal.keras"))
cnn_image_only = tf.keras.models.load_model(os.path.join(MODEL_DIR, "cnn_image_only.keras"))
with open(os.path.join(MODEL_DIR, "cnn_metadata.json"), "r", encoding="utf-8") as f:
    cnn_metadata = json.load(f)

print("Modeles charges avec succes")

# ============================================
# Schemas
# ============================================
class PatientData(BaseModel):
    age: int
    sexe_masculin: int
    presence_nodule: int
    subtilite_nodule: int
    taille_nodule_px: int
    x_nodule_norm: float
    y_nodule_norm: float
    tabagisme_paquets_annee: float
    toux_chronique: int
    dyspnee: int
    douleur_thoracique: int
    perte_poids: int
    spo2: int
    antecedent_familial: int


class TabularPrediction(BaseModel):
    risque_predit: int
    risque_label: str
    probabilites: dict
    model_utilise: str


class CancerPrediction(BaseModel):
    cancer_probable: bool
    probabilite_cancer: float
    risque_tabulaire: dict
    verdict: str
    mode: str  # "multimodal" ou "image_only"


# ============================================
# Helpers
# ============================================
def tabular_to_vector(patient: PatientData) -> np.ndarray:
    return np.array([[
        patient.age, patient.sexe_masculin, patient.presence_nodule,
        patient.subtilite_nodule, patient.taille_nodule_px,
        patient.x_nodule_norm, patient.y_nodule_norm,
        patient.tabagisme_paquets_annee, patient.toux_chronique,
        patient.dyspnee, patient.douleur_thoracique, patient.perte_poids,
        patient.spo2, patient.antecedent_familial,
    ]], dtype=np.float32)


def preprocess_image_file(file_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(img, dtype=np.float32)
    arr = preprocess_input(arr)
    return np.expand_dims(arr, axis=0)


# ============================================
# Endpoints
# ============================================
@app.get("/")
def root():
    return {
        "message": "API Cancer Pulmonaire",
        "endpoints": {
            "health": "/api/health",
            "predict_tabular": "POST /api/predict-tabular",
            "predict_cancer": "POST /api/predict-cancer (multipart: image + champs patient)",
        },
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "tabular_model": tabular_metadata["best_model"],
        "tabular_accuracy": tabular_metadata["results"][tabular_metadata["best_model"]]["test_accuracy"],
        "cnn_multimodal_f1": cnn_metadata["multimodal"]["f1"],
        "cnn_image_only_f1": cnn_metadata["image_only"]["f1"],
    }


@app.post("/api/predict-tabular", response_model=TabularPrediction)
def predict_tabular(patient: PatientData):
    X = tabular_to_vector(patient)
    pred = int(tabular_model.predict(X)[0])
    probas = tabular_model.predict_proba(X)[0]
    return TabularPrediction(
        risque_predit=pred,
        risque_label=RISQUE_LABELS[pred],
        probabilites={
            "Faible": float(probas[0]),
            "Intermediaire": float(probas[1]),
            "Eleve": float(probas[2]),
        },
        model_utilise=tabular_metadata["best_model"],
    )


@app.post("/api/predict-cancer", response_model=CancerPrediction)
async def predict_cancer(
    image: UploadFile = File(...),
    age: int = Form(...),
    sexe_masculin: int = Form(...),
    presence_nodule: int = Form(...),
    subtilite_nodule: int = Form(...),
    taille_nodule_px: int = Form(...),
    x_nodule_norm: float = Form(...),
    y_nodule_norm: float = Form(...),
    tabagisme_paquets_annee: float = Form(...),
    toux_chronique: int = Form(...),
    dyspnee: int = Form(...),
    douleur_thoracique: int = Form(...),
    perte_poids: int = Form(...),
    spo2: int = Form(...),
    antecedent_familial: int = Form(...),
    mode: str = Form("multimodal"),  # multimodal | image_only
):
    # Validation type image
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit etre une image")

    img_bytes = await image.read()
    img_arr = preprocess_image_file(img_bytes)

    # Construire le vecteur tabulaire
    patient = PatientData(
        age=age, sexe_masculin=sexe_masculin, presence_nodule=presence_nodule,
        subtilite_nodule=subtilite_nodule, taille_nodule_px=taille_nodule_px,
        x_nodule_norm=x_nodule_norm, y_nodule_norm=y_nodule_norm,
        tabagisme_paquets_annee=tabagisme_paquets_annee,
        toux_chronique=toux_chronique, dyspnee=dyspnee,
        douleur_thoracique=douleur_thoracique, perte_poids=perte_poids,
        spo2=spo2, antecedent_familial=antecedent_familial,
    )
    X_tab = tabular_to_vector(patient)
    tab_probas = tabular_model.predict_proba(X_tab)
    tab_pred = int(tabular_model.predict(X_tab)[0])

    # Prediction
    if mode == "multimodal":
        cancer_proba = float(cnn_multimodal.predict(
            [img_arr, tab_probas.astype(np.float32)], verbose=0
        ).ravel()[0])
    else:
        cancer_proba = float(cnn_image_only.predict(img_arr, verbose=0).ravel()[0])

    cancer_probable = cancer_proba > 0.5
    verdict = (
        "Cancer pulmonaire probable - consultation specialiste recommandee"
        if cancer_probable
        else "Cancer pulmonaire non probable - surveillance standard"
    )

    return CancerPrediction(
        cancer_probable=cancer_probable,
        probabilite_cancer=cancer_proba,
        risque_tabulaire={
            "niveau": RISQUE_LABELS[tab_pred],
            "faible": float(tab_probas[0][0]),
            "intermediaire": float(tab_probas[0][1]),
            "eleve": float(tab_probas[0][2]),
        },
        verdict=verdict,
        mode=mode,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
