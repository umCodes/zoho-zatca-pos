import type { CustomerDetail } from "../types";

// Saudi CRN: 10 digits — legacy commercial registration numbers start with
// "1", the post-2026 unified national registration starts with "7".
export const CRN_PATTERN = /^[17]\d{9}$/;
// Saudi VAT/TRN: 15 digits — first digit is the GCC member-state code (3 for
// Saudi Arabia) and the number also ends in 3 (tax-type suffix), per ZATCA's
// published format and verified against a real customer's TRN on file.
export const VAT_PATTERN = /^3\d{13}3$/;

export type CustomerIssue =
  | "notVatRegistered"
  | "missingVat"
  | "missingCrn"
  | "missingAddress";

// ZATCA Standard Tax Invoice (B2B) requires the buyer's VAT registration
// number, CRN, and address — verified against a real complete customer
// record (Abdulaziz Abdul Latif Saleh Al-Hussein Trading Est.) and ZATCA's
// published e-invoicing guidelines.
export function validateCustomerForB2B(customer: CustomerDetail): CustomerIssue[] {
  const issues: CustomerIssue[] = [];

  if (customer.tax_treatment !== "vat_registered") {
    issues.push("notVatRegistered");
  }
  if (!VAT_PATTERN.test((customer.tax_reg_no || "").trim())) {
    issues.push("missingVat");
  }
  if (!CRN_PATTERN.test((customer.buyer_id_value || "").trim())) {
    issues.push("missingCrn");
  }

  const a = customer.billing_address;
  const addressComplete = !!(
    a &&
    a.street2?.trim() &&
    a.city?.trim() &&
    a.district?.trim() &&
    a.state?.trim() &&
    a.zip?.trim() &&
    a.country?.trim()
  );
  if (!addressComplete) {
    issues.push("missingAddress");
  }

  return issues;
}
