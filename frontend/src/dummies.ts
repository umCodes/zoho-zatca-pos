

export async function submitInvoice(): Promise<{
  invoice_id: string;
  invoice_number: string;
}> {
  // ── Dummy: simulates network delay ───────────────────────────────────────
  await new Promise((resolve) => setTimeout(resolve, 1500));
  return {
    invoice_id: "46324000000100197",
    invoice_number: "INV-00042",
  };
}
