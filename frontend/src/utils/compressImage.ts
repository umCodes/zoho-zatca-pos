// Client-side image compression for document scans.
//
// The backend runs on a tiny Render instance, so all image work happens here
// in the browser: photos are downscaled and re-encoded as JPEG before upload.
// A typical 4–8 MB phone photo becomes ~200–500 KB, which is still plenty for
// OCR on an A4 certificate. PDFs and anything the browser can't decode
// (e.g. HEIC on non-Safari browsers) are sent unchanged — the OCR service
// accepts those formats directly.

const MAX_DIMENSION = 2000; // px on the longest side — keeps small print legible
const JPEG_QUALITY = 0.82;
// Already-small JPEGs aren't worth re-encoding (re-encoding only loses detail).
const SKIP_BELOW_BYTES = 350 * 1024;

async function decode(file: File): Promise<ImageBitmap | HTMLImageElement> {
  if ("createImageBitmap" in window) {
    try {
      // imageOrientation honours EXIF rotation so phone photos aren't sideways.
      return await createImageBitmap(file, { imageOrientation: "from-image" });
    } catch {
      /* fall through to <img> decoding */
    }
  }
  const url = URL.createObjectURL(file);
  try {
    const img = new Image();
    img.src = url;
    await img.decode();
    return img;
  } finally {
    URL.revokeObjectURL(url);
  }
}

export async function compressImage(file: File): Promise<File> {
  if (!file.type.startsWith("image/")) return file;
  if (file.type === "image/jpeg" && file.size <= SKIP_BELOW_BYTES) return file;

  let source: ImageBitmap | HTMLImageElement;
  try {
    source = await decode(file);
  } catch {
    return file; // undecodable here (e.g. HEIC in Chrome) — let the server/OCR handle it
  }

  const srcW = source instanceof HTMLImageElement ? source.naturalWidth : source.width;
  const srcH = source instanceof HTMLImageElement ? source.naturalHeight : source.height;
  const scale = Math.min(1, MAX_DIMENSION / Math.max(srcW, srcH));
  const w = Math.max(1, Math.round(srcW * scale));
  const h = Math.max(1, Math.round(srcH * scale));

  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) return file;
  // White background so transparent PNGs don't turn black as JPEG.
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, w, h);
  ctx.drawImage(source, 0, 0, w, h);
  if ("close" in source) source.close();

  const blob = await new Promise<Blob | null>((resolve) =>
    canvas.toBlob(resolve, "image/jpeg", JPEG_QUALITY),
  );
  // Release the canvas backing store promptly (matters on low-memory tablets).
  canvas.width = canvas.height = 0;

  if (!blob || blob.size >= file.size) return file;
  const name = file.name.replace(/\.[^.]+$/, "") + ".jpg";
  return new File([blob], name, { type: "image/jpeg", lastModified: file.lastModified });
}

/** Compresses files one at a time so only one decoded image is in memory at once. */
export async function compressImages(files: File[]): Promise<File[]> {
  const out: File[] = [];
  for (const f of files) out.push(await compressImage(f));
  return out;
}
