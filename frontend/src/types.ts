

export type Item = {
    item_id: string;
    name: string;
    status: string;
    description: string;
    rate: number;
    unit: string;
    tax_id: string;
    tax_name: string;
    tax_percentage: number;
    sku: string;
    qty?: number;
}





export type CartRow = {
  item_id: string
  name: string
  rate: number      // VAT-inclusive
  quantity: number
  unit: string
}

export type ToastState = {
  message: string
  type: 'success' | 'error'
}

export type Lang = 'en' | 'ar' | 'am'

export type Customer = {
  contact_id: string
  contact_type: 'customer'
  tax_reg_no: string
  contact_name: string
}

// We only ever create customers with a CRN — no user-facing ID-type choice.
export const BUYER_ID_LABEL = 'CRN' as const;

// building_number / additional_number / zip are digit strings — identical in
// both languages, so they're a single shared field (no _sec_lang twin) that's
// mirrored onto both Zoho fields when saving. street/district/city/state/country
// are real text that differs by language and gets AR->EN auto-translation.
export interface CustomerAddressForm {
  building_number: string
  additional_number: string
  zip: string
  street: string
  street_sec_lang: string
  district: string
  district_sec_lang: string
  city: string
  city_sec_lang: string
  state: string
  state_sec_lang: string
  country: string
  country_sec_lang: string
}

export interface CreateCustomerForm {
  contact_name: string             // Arabic — primary
  contact_name_sec_lang: string    // English — secondary
  tax_reg_no: string                // VAT — required
  buyer_id_value: string             // CRN — required
  billing_address: CustomerAddressForm
}

export const DEFAULT_COUNTRY_AR = 'المملكة العربية السعودية';
export const DEFAULT_COUNTRY_EN = 'Saudi Arabia';
export const DEFAULT_CITY_AR = 'الرياض';
export const DEFAULT_CITY_EN = 'Riyadh';
// Verified against real Zoho customer records — Zoho's state field for
// Riyadh region is stored as "Ar Riyad" (their own transliteration), not
// "Riyadh" — used for both language slots since Zoho itself doesn't
// differentiate the region name per language.
export const DEFAULT_STATE_AR = 'الرياض';
export const DEFAULT_STATE_EN = 'Ar Riyad';

export const emptyCustomerAddress = (): CustomerAddressForm => ({
  building_number: '',
  additional_number: '',
  zip: '',
  street: '',
  street_sec_lang: '',
  district: '',
  district_sec_lang: '',
  city: DEFAULT_CITY_AR,
  city_sec_lang: DEFAULT_CITY_EN,
  state: DEFAULT_STATE_AR,
  state_sec_lang: DEFAULT_STATE_EN,
  country: DEFAULT_COUNTRY_AR,
  country_sec_lang: DEFAULT_COUNTRY_EN,
})

export const emptyCreateCustomerForm = (): CreateCustomerForm => ({
  contact_name: '',
  contact_name_sec_lang: '',
  tax_reg_no: '',
  buyer_id_value: '',
  billing_address: emptyCustomerAddress(),
})