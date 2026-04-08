"use client";

import type { PatientData } from "@/lib/types";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";

type Props = {
  patient: PatientData;
  onChange: (patient: PatientData) => void;
};

export function PatientFields({ patient, onChange }: Props) {
  const update = <K extends keyof PatientData>(key: K, value: PatientData[K]) =>
    onChange({ ...patient, [key]: value });

  return (
    <div className="space-y-6">
      {/* Démographie */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wider">
          Démographie
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="age">Âge</Label>
            <Input
              id="age"
              type="number"
              min={1}
              max={120}
              value={patient.age}
              onChange={(e) => update("age", Number(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="sexe">Sexe</Label>
            <Select
              value={String(patient.sexe_masculin)}
              onValueChange={(v) => update("sexe_masculin", Number(v))}
            >
              <SelectTrigger id="sexe">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Masculin</SelectItem>
                <SelectItem value="0">Féminin</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Separator />

      {/* Nodule */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wider">
          Caractéristiques du nodule
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2 sm:col-span-2 flex items-center justify-between rounded-lg border border-border p-3">
            <div>
              <Label htmlFor="presence_nodule" className="text-sm">
                Nodule détecté
              </Label>
              <p className="text-xs text-muted-foreground mt-1">
                Présence d&apos;un nodule à la radiographie
              </p>
            </div>
            <Switch
              id="presence_nodule"
              checked={patient.presence_nodule === 1}
              onCheckedChange={(c) => update("presence_nodule", c ? 1 : 0)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="subtilite_nodule">Subtilité (1-5)</Label>
            <Input
              id="subtilite_nodule"
              type="number"
              min={1}
              max={5}
              value={patient.subtilite_nodule}
              onChange={(e) => update("subtilite_nodule", Number(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="taille_nodule_px">Taille (px)</Label>
            <Input
              id="taille_nodule_px"
              type="number"
              min={0}
              value={patient.taille_nodule_px}
              onChange={(e) =>
                update("taille_nodule_px", Number(e.target.value))
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="x_nodule_norm">Position X (0-1)</Label>
            <Input
              id="x_nodule_norm"
              type="number"
              step="0.01"
              min={0}
              max={1}
              value={patient.x_nodule_norm}
              onChange={(e) => update("x_nodule_norm", Number(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="y_nodule_norm">Position Y (0-1)</Label>
            <Input
              id="y_nodule_norm"
              type="number"
              step="0.01"
              min={0}
              max={1}
              value={patient.y_nodule_norm}
              onChange={(e) => update("y_nodule_norm", Number(e.target.value))}
            />
          </div>
        </div>
      </div>

      <Separator />

      {/* Symptômes cliniques */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wider">
          Signes cliniques
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="tabagisme">Tabagisme (paquets-années)</Label>
            <Input
              id="tabagisme"
              type="number"
              step="0.1"
              min={0}
              value={patient.tabagisme_paquets_annee}
              onChange={(e) =>
                update("tabagisme_paquets_annee", Number(e.target.value))
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="spo2">SpO₂ (%)</Label>
            <Input
              id="spo2"
              type="number"
              min={50}
              max={100}
              value={patient.spo2}
              onChange={(e) => update("spo2", Number(e.target.value))}
            />
          </div>

          {[
            { key: "toux_chronique", label: "Toux chronique" },
            { key: "dyspnee", label: "Dyspnée" },
            { key: "douleur_thoracique", label: "Douleur thoracique" },
            { key: "perte_poids", label: "Perte de poids" },
            { key: "antecedent_familial", label: "Antécédent familial" },
          ].map(({ key, label }) => (
            <div
              key={key}
              className="flex items-center justify-between rounded-lg border border-border p-3"
            >
              <Label htmlFor={key} className="text-sm cursor-pointer">
                {label}
              </Label>
              <Switch
                id={key}
                checked={patient[key as keyof PatientData] === 1}
                onCheckedChange={(c) =>
                  update(key as keyof PatientData, (c ? 1 : 0) as never)
                }
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
