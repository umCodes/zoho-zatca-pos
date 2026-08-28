/**
 * Fetches a PDF and opens the browser's native print dialog directly,
 * with no visible intermediate tab. Loads the PDF into a hidden iframe via
 * a blob: URL (same-origin to the page, so contentWindow.print() is allowed
 * regardless of where the PDF itself was served from) and triggers print
 * once the iframe has actually rendered the file.
 */
export async function printPdf(url: string, headers?: Record<string, string>): Promise<void> {
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const blob = await res.blob();
  const blobUrl = URL.createObjectURL(blob);

  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.width = "0";
  iframe.style.height = "0";
  iframe.style.border = "none";
  iframe.style.visibility = "hidden";

  const cleanup = () => {
    iframe.remove();
    URL.revokeObjectURL(blobUrl);
  };

  iframe.onload = () => {
    try {
      iframe.contentWindow?.focus();
      iframe.contentWindow?.print();
    } catch (err) {
      console.error("Failed to open print dialog:", err);
    }
    // The print dialog is modal, so the iframe only needs to survive long
    // enough to have been focused into it — clean up shortly after.
    setTimeout(cleanup, 1000);
  };

  iframe.src = blobUrl;
  document.body.appendChild(iframe);
}
