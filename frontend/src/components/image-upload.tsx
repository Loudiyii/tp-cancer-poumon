"use client";

import { useRef, useState } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Upload, X } from "lucide-react";

type Props = {
  onImageChange: (file: File | null) => void;
};

export function ImageUpload({ onImageChange }: Props) {
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File | null) => {
    if (!file) {
      setPreview(null);
      setFileName(null);
      onImageChange(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    setFileName(file.name);
    onImageChange(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    handleFile(file);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0] ?? null;
    if (file && file.type.startsWith("image/")) {
      handleFile(file);
    }
  };

  const clear = () => {
    handleFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="space-y-3">
      <Label>Radiographie thoracique</Label>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleInputChange}
      />

      {!preview ? (
        <div
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
          }}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="flex flex-col items-center justify-center w-full h-56 rounded-lg border-2 border-dashed border-border bg-card/50 hover:bg-accent/40 transition cursor-pointer"
        >
          <Upload className="h-8 w-8 text-muted-foreground mb-2" />
          <p className="text-sm font-medium text-foreground">
            Cliquer ou glisser une image
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            JPG, PNG — radiographie du thorax
          </p>
        </div>
      ) : (
        <div className="relative rounded-lg overflow-hidden border border-border bg-black">
          <Image
            src={preview}
            alt="Radio"
            width={512}
            height={512}
            unoptimized
            className="w-full h-56 object-contain"
          />
          <Button
            type="button"
            size="icon"
            variant="secondary"
            onClick={clear}
            className="absolute top-2 right-2 h-7 w-7 rounded-full"
          >
            <X className="h-4 w-4" />
          </Button>
          {fileName && (
            <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs px-3 py-1 truncate">
              {fileName}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
