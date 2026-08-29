export type LineItemIssue = "missingRate" | "missingNameEn" | "missingNameAr" | "missingDescription";

interface ValidatableLineItem {
  rate: number;
  name: string;
  name_sec_lang?: string;
  description?: string;
}

// ZATCA Standard Tax Invoice (B2B) line items need a rate, both bilingual
// names, and a description — verified against live, already-pushed items
// (e.g. "بخور عدني وسط" / "Adeni Medium Incense") and the auto-heal logic in
// push_to_fatoora, which specifically repairs items missing name_sec_lang.
export function validateLineItem(entry: ValidatableLineItem): LineItemIssue[] {
  const issues: LineItemIssue[] = [];
  if (!entry.rate || entry.rate <= 0) issues.push("missingRate");
  if (!entry.name?.trim()) issues.push("missingNameAr");
  if (!entry.name_sec_lang?.trim()) issues.push("missingNameEn");
  if (!entry.description?.trim()) issues.push("missingDescription");
  return issues;
}
