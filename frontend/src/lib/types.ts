export interface PatientData {
  age: number;
  sexe_masculin: number;
  presence_nodule: number;
  subtilite_nodule: number;
  taille_nodule_px: number;
  x_nodule_norm: number;
  y_nodule_norm: number;
  tabagisme_paquets_annee: number;
  toux_chronique: number;
  dyspnee: number;
  douleur_thoracique: number;
  perte_poids: number;
  spo2: number;
  antecedent_familial: number;
}

export interface TabularPrediction {
  risque_predit: number;
  risque_label: string;
  probabilites: {
    Faible: number;
    Intermediaire: number;
    Eleve: number;
  };
  model_utilise: string;
}

export interface CancerPrediction {
  cancer_probable: boolean;
  probabilite_cancer: number;
  risque_tabulaire: {
    niveau: string;
    faible: number;
    intermediaire: number;
    eleve: number;
  };
  verdict: string;
  mode: "multimodal" | "image_only";
}

export interface HealthResponse {
  status: string;
  tabular_model: string;
  tabular_accuracy: number;
  cnn_multimodal_f1: number;
  cnn_image_only_f1: number;
}
