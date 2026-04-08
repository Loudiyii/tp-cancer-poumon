"use client";

import { useState } from "react";
import { toast } from "sonner";
import { PatientFields } from "./patient-fields";
import { ImageUpload } from "./image-upload";
import { ResultDisplay } from "./result-display";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Activity, Loader2, Sparkles, Stethoscope } from "lucide-react";
import { predictCancer } from "@/lib/api";
import type { CancerPrediction, PatientData } from "@/lib/types";

const INITIAL_PATIENT: PatientData = {
  age: 62,
  sexe_masculin: 1,
  presence_nodule: 1,
  subtilite_nodule: 4,
  taille_nodule_px: 1,
  x_nodule_norm: 0.5,
  y_nodule_norm: 0.4,
  tabagisme_paquets_annee: 30,
  toux_chronique: 1,
  dyspnee: 1,
  douleur_thoracique: 1,
  perte_poids: 1,
  spo2: 92,
  antecedent_familial: 0,
};

export function PredictionTool() {
  const [patient, setPatient] = useState<PatientData>(INITIAL_PATIENT);
  const [image, setImage] = useState<File | null>(null);
  const [mode, setMode] = useState<"multimodal" | "image_only">("multimodal");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CancerPrediction | null>(null);

  async function onPredict() {
    if (!image) {
      toast.error("Veuillez uploader une radiographie thoracique.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const prediction = await predictCancer(patient, image, mode);
      setResult(prediction);
      toast.success("Prédiction effectuée");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erreur inconnue";
      toast.error(`Échec de la prédiction : ${msg}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
      {/* Colonne formulaire */}
      <div className="lg:col-span-3 space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Stethoscope className="h-5 w-5 text-primary" />
                  Données cliniques du patient
                </CardTitle>
                <CardDescription className="mt-1">
                  Renseignez les informations démographiques et les signes cliniques
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <PatientFields patient={patient} onChange={setPatient} />
          </CardContent>
        </Card>
      </div>

      {/* Colonne image + actions */}
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Imagerie médicale
            </CardTitle>
            <CardDescription>
              Charger la radiographie thoracique pour analyse
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <ImageUpload onImageChange={setImage} />

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Mode de prédiction
              </label>
              <Tabs
                value={mode}
                onValueChange={(v) =>
                  setMode(v as "multimodal" | "image_only")
                }
              >
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="multimodal" className="text-xs">
                    <Sparkles className="h-3 w-3 mr-1" />
                    Multimodal
                  </TabsTrigger>
                  <TabsTrigger value="image_only" className="text-xs">
                    Image seule
                  </TabsTrigger>
                </TabsList>
              </Tabs>
              <p className="text-xs text-muted-foreground">
                {mode === "multimodal"
                  ? "Fusion : image + probabilités du modèle tabulaire"
                  : "CNN classique basé uniquement sur la radio"}
              </p>
            </div>

            <Button
              onClick={onPredict}
              disabled={loading || !image}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyse en cours…
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Lancer la prédiction
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {result && <ResultDisplay result={result} />}
      </div>
    </div>
  );
}
