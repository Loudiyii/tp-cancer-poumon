import type {
  CancerPrediction,
  HealthResponse,
  PatientData,
  TabularPrediction,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "https://tp-cancer-poumon.onrender.com");

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/api/health`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API health failed: ${res.status}`);
  return res.json();
}

export async function predictTabular(
  data: PatientData
): Promise<TabularPrediction> {
  const res = await fetch(`${API_URL}/api/predict-tabular`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Predict tabular failed: ${res.status}`);
  return res.json();
}

export async function predictCancer(
  patient: PatientData,
  image: File,
  mode: "multimodal" | "image_only"
): Promise<CancerPrediction> {
  const formData = new FormData();
  formData.append("image", image);
  formData.append("mode", mode);
  Object.entries(patient).forEach(([key, value]) => {
    formData.append(key, String(value));
  });

  const res = await fetch(`${API_URL}/api/predict-cancer`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Predict cancer failed: ${res.status} - ${text}`);
  }
  return res.json();
}
