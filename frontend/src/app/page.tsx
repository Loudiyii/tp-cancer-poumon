import { PredictionTool } from "@/components/prediction-tool";
import { Badge } from "@/components/ui/badge";
import { Brain, Microscope, Sparkles } from "lucide-react";

export default function HomePage() {
  return (
    <div className="relative min-h-screen">
      {/* Subtle gradient background */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.08),transparent_60%)]"
      />

      <main className="relative mx-auto max-w-6xl px-6 py-10 sm:py-16">
        {/* Header */}
        <header className="mb-10 sm:mb-14">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
                <Microscope className="h-5 w-5 text-primary" />
              </div>
              <span className="text-lg font-semibold tracking-tight">
                Pulmo<span className="text-primary">AI</span>
              </span>
            </div>
            <Badge
              variant="outline"
              className="font-mono text-[10px] uppercase tracking-wider"
            >
              TP — M2 ESIC · MLOps
            </Badge>
          </div>

          <div className="max-w-3xl">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-xs font-medium text-primary uppercase tracking-wider">
                Intelligence artificielle médicale
              </span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-bold tracking-tight text-foreground mb-4">
              Détection du cancer pulmonaire{" "}
              <span className="text-primary">multimodale</span>
            </h1>
            <p className="text-base sm:text-lg text-muted-foreground leading-relaxed">
              Plateforme de prédiction fusionnant{" "}
              <span className="text-foreground font-medium">
                données cliniques
              </span>{" "}
              et{" "}
              <span className="text-foreground font-medium">
                radiographies thoraciques
              </span>{" "}
              via un modèle de machine learning et un réseau de neurones
              convolutif.
            </p>

            <div className="mt-6 flex flex-wrap gap-2">
              <Badge variant="secondary" className="text-xs">
                <Brain className="h-3 w-3 mr-1" />
                MobileNetV2 fine-tuned
              </Badge>
              <Badge variant="secondary" className="text-xs">
                LogisticRegression
              </Badge>
              <Badge variant="secondary" className="text-xs">
                Fusion multimodale
              </Badge>
              <Badge variant="secondary" className="text-xs">
                FastAPI · Next.js
              </Badge>
            </div>
          </div>
        </header>

        {/* Tool */}
        <PredictionTool />

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-border">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-muted-foreground">
            <p>
              Développé dans le cadre du TP noté MLOps — M2 ESIC IA/ML/DL ·
              2025-2026
            </p>
            <p className="font-mono">Professeur : Redouane FENZI</p>
          </div>
          <p className="mt-4 text-[11px] text-muted-foreground/70 italic">
            ⚠ Outil éducatif uniquement — ne remplace en aucun cas un avis
            médical professionnel.
          </p>
        </footer>
      </main>
    </div>
  );
}
