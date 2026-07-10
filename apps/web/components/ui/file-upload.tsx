"use client";

import { FileUp, Loader2, RotateCcw, X } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type FileUploadCategory = "resume" | "document" | "image";

type FileUploadProps = {
  accept?: string;
  category?: FileUploadCategory;
  disabled?: boolean;
  label?: string;
  hint?: string;
  onUpload: (file: File, onProgress: (pct: number) => void) => Promise<void>;
  className?: string;
};

const DEFAULT_ACCEPT: Record<FileUploadCategory, string> = {
  resume:
    ".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  document:
    ".pdf,.doc,.docx,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg",
  image: ".png,.jpg,.jpeg,image/png,image/jpeg",
};

export function FileUpload({
  accept,
  category = "document",
  disabled,
  label = "Drop a file here or click to browse",
  hint,
  onUpload,
  className,
}: FileUploadProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = React.useState(false);
  const [file, setFile] = React.useState<File | null>(null);
  const [progress, setProgress] = React.useState(0);
  const [status, setStatus] = React.useState<
    "idle" | "uploading" | "done" | "error"
  >("idle");
  const [error, setError] = React.useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!file || !file.type.startsWith("image/")) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const reset = () => {
    setFile(null);
    setProgress(0);
    setStatus("idle");
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const startUpload = async (next: File) => {
    setFile(next);
    setStatus("uploading");
    setProgress(0);
    setError(null);
    try {
      await onUpload(next, setProgress);
      setStatus("done");
      setProgress(100);
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  };

  const onSelect = (list: FileList | null) => {
    const next = list?.[0];
    if (!next || disabled) return;
    void startUpload(next);
  };

  return (
    <div className={cn("space-y-3", className)}>
      <div
        role="button"
        tabIndex={0}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed px-4 py-8 text-center transition-colors",
          dragOver && "border-primary bg-muted/40",
          disabled && "pointer-events-none opacity-50",
          status === "error" && "border-destructive",
        )}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          onSelect(e.dataTransfer.files);
        }}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={accept ?? DEFAULT_ACCEPT[category]}
          disabled={disabled || status === "uploading"}
          onChange={(e) => onSelect(e.target.files)}
        />
        {status === "uploading" ? (
          <Loader2 className="text-muted-foreground mb-2 h-8 w-8 animate-spin" />
        ) : (
          <FileUp className="text-muted-foreground mb-2 h-8 w-8" />
        )}
        <p className="text-sm font-medium">{label}</p>
        {hint && <p className="text-muted-foreground mt-1 text-xs">{hint}</p>}
      </div>

      {file && (
        <div className="rounded-md border px-3 py-2 text-sm">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate font-medium">{file.name}</p>
              <p className="text-muted-foreground text-xs">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={reset}
              disabled={status === "uploading"}
              aria-label="Clear file"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {previewUrl && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={previewUrl}
              alt="Preview"
              className="mt-2 max-h-40 rounded-md object-contain"
            />
          )}

          {(status === "uploading" || status === "done") && (
            <div className="mt-2">
              <div className="bg-muted h-2 overflow-hidden rounded-full">
                <div
                  className="bg-primary h-full transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-muted-foreground mt-1 text-xs">
                {status === "done" ? "Uploaded" : `${progress}%`}
              </p>
            </div>
          )}

          {status === "error" && (
            <div className="mt-2 flex items-center justify-between gap-2">
              <p className="text-destructive text-xs">{error}</p>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => file && void startUpload(file)}
              >
                <RotateCcw className="mr-1 h-3 w-3" />
                Retry
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/** Upload via XHR so progress events work through the Next BFF proxy. */
export function uploadWithProgress(
  url: string,
  form: FormData,
  onProgress: (pct: number) => void,
): Promise<Response> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.withCredentials = true;
    xhr.upload.onprogress = (event) => {
      if (!event.lengthComputable) return;
      onProgress(Math.min(99, Math.round((event.loaded / event.total) * 100)));
    };
    xhr.onload = () => {
      const headers = new Headers();
      const contentType = xhr.getResponseHeader("Content-Type");
      if (contentType) headers.set("Content-Type", contentType);
      resolve(
        new Response(xhr.responseText, {
          status: xhr.status,
          statusText: xhr.statusText,
          headers,
        }),
      );
    };
    xhr.onerror = () => reject(new Error("Network error during upload"));
    xhr.send(form);
  });
}

export async function parseUploadError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { message?: string };
    if (data.message) return data.message;
  } catch {
    // ignore
  }
  return `Upload failed (${response.status})`;
}
