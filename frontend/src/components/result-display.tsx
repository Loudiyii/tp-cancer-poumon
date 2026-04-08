"use client";

import type { CancerPrediction } from "@/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, CheckCircle2, Activity, Brain, Image as ImageIcon } from "lucide-react";

type Props = { result: CancerPrediction };

export function ResultDisplay({ result }: Props) {
  const isPositive = result.cancer_probable;
  const pct = (result.probabilite_cancer * 100).toFixed(1);
  const riskColors: Record<string, string> = {
    Faible: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    Intermediaire: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    Eleve: "bg-red-500/20 text-red-400 border-red-500/30",
  };

  return (
    <div className="space-y-4">
      {/* Alert principale */}
      <Alert
        className={
          isPositive
            ? "border-red-500/40 bg-red-500/10"
            : "border-emerald-500/40 bg-emerald-500/10"
        }
      >
        {isPositive ? (
          <AlertCircle className="h-5 w-5 text-red-400" />
        ) : (
          <CheckCircle2 className="h-5 w-5 text-emerald-400" />
        )}
        <AlertTitle className="text-base font-semibold">
          {isPositive ? "Cancer pulmonaire probable" : "Cancer pulmonaire non probable"}
        </AlertTitle>
        <AlertDescription className="text-sm mt-1 text-foreground/80">
          {result.verdict}
        </AlertDescription>
      </Alert>

      {/* Probabilité CNN */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {result.mode === "multimodal" ? (
                <Brain className="h-4 w-4 text-primary" />
              ) : (
                <ImageIcon className="h-4 w-4 text-primary" />
              )}
              <CardTitle className="text-sm font-semibold">
                Modèle {result.mode === "multimodal" ? "multimodal" : "image seule"}
              </CardTitle>
            </div>
            <Badge variant="outline" className="font-mono text-xs">
              CNN
            </Badge>
          </div>
          <CardDescription className="text-xs mt-1">
            Probabilité de cancer estimée par le réseau de neurones
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-bold font-mono">{pct}%</span>
            <span className="text-xs text-muted-foreground">probabilité</span>
          </div>
          <Progress value={Number(pct)} className="h-2" />
        </CardContent>
      </Card>

      {/* Modèle tabulaire */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              <CardTitle className="text-sm font-semibold">
                Risque clinique (tabulaire)
              </CardTitle>
            </div>
            <Badge
              className={`${riskColors[result.risque_tabulaire.niveau] ?? ""} font-medium`}
              variant="outline"
            >
              {result.risque_tabulaire.niveau}
            </Badge>
          </div>
          <CardDescription className="text-xs mt-1">
            Prédiction à partir des données patient uniquement
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {[
            {
              label: "Faible",
              value: result.risque_tabulaire.faible,
              color: "bg-emerald-500",
            },
            {
              label: "Intermédiaire",
              value: result.risque_tabulaire.intermediaire,
              color: "bg-amber-500",
            },
            {
              label: "Élevé",
              value: result.risque_tabulaire.eleve,
              color: "bg-red-500",
            },
          ].map(({ label, value, color }) => (
            <div key={label} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">{label}</span>
                <span className="font-mono font-medium">
                  {(value * 100).toFixed(1)}%
                </span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full ${color} transition-all`}
                  style={{ width: `${value * 100}%` }}
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
