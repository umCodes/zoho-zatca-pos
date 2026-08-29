import { useRef, useState } from "react";
import { Upload, X, ChevronDown, ScanLine } from "lucide-react";
import "../styles/CreateCustomerModal.css";
import { useLocale } from "../context/LangContext";
import { usePassword } from "../context/PasswordContext";
import { apiUrl } from "../env";
import {
  emptyCreateCustomerForm,
  type Customer,
  type CreateCustomerForm,
  type CustomerAddressForm,
} from "../types";
import { CRN_PATTERN, VAT_PATTERN } from "../utils/customerValidation";

interface CreateCustomerModalProps {
  isOpen: boolean;
  initialQuery?: string;
  onClose: () => void;
  onCreated: (customer: Customer) => void;
}

// Saudi Arabia's 13 administrative regions — Zoho stores the Riyadh region as
// "Ar Riyad" / "الرياض" (verified against a live customer record), so the
// English list below matches Zoho's own transliteration rather than the more
// common English spelling, to keep saved data consistent with existing contacts.
const SAUDI_STATES: { ar: string; en: string }[] = [
  { ar: "الرياض", en: "Ar Riyad" },
  { ar: "مكة المكرمة", en: "Makkah" },
  { ar: "المدينة المنورة", en: "Al Madinah" },
  { ar: "القصيم", en: "Al Qassim" },
  { ar: "المنطقة الشرقية", en: "Eastern Province" },
  { ar: "عسير", en: "Asir" },
  { ar: "تبوك", en: "Tabuk" },
  { ar: "حائل", en: "Hail" },
  { ar: "الحدود الشمالية", en: "Northern Borders" },
  { ar: "جازان", en: "Jazan" },
  { ar: "نجران", en: "Najran" },
  { ar: "الباحة", en: "Al Bahah" },
  { ar: "الجوف", en: "Al Jouf" },
];

const SAUDI_CITIES: { ar: string; en: string }[] = [
  { ar: "الرياض", en: "Riyadh" },
  { ar: "جدة", en: "Jeddah" },
  { ar: "مكة المكرمة", en: "Makkah" },
  { ar: "المدينة المنورة", en: "Madinah" },
  { ar: "الدمام", en: "Dammam" },
  { ar: "الخبر", en: "Khobar" },
  { ar: "الظهران", en: "Dhahran" },
  { ar: "تبوك", en: "Tabuk" },
  { ar: "بريدة", en: "Buraidah" },
  { ar: "خميس مشيط", en: "Khamis Mushait" },
  { ar: "أبها", en: "Abha" },
  { ar: "حائل", en: "Hail" },
  { ar: "نجران", en: "Najran" },
  { ar: "جازان", en: "Jazan" },
  { ar: "الجبيل", en: "Jubail" },
  { ar: "ينبع", en: "Yanbu" },
  { ar: "الطائف", en: "Taif" },
];

const COUNTRIES: { ar: string; en: string }[] = [
  { ar: "المملكة العربية السعودية", en: "Saudi Arabia" },
  { ar: "الإمارات العربية المتحدة", en: "United Arab Emirates" },
  { ar: "البحرين", en: "Bahrain" },
  { ar: "الكويت", en: "Kuwait" },
  { ar: "عمان", en: "Oman" },
  { ar: "قطر", en: "Qatar" },
];

type SharedAddressField = "building_number" | "additional_number" | "zip";
type TranslatablePair =
  | "street" | "district" | "city" | "state" | "country";
type TranslatableFormField = "name";

type SectionKey = "identification" | "address";

const DEBOUNCE_MS = 700;

export default function CreateCustomerModal({
  isOpen,
  initialQuery,
  onClose,
  onCreated,
}: CreateCustomerModalProps) {
  const { t } = useLocale();
  const { password } = usePassword();

  const [form, setForm] = useState<CreateCustomerForm>(() => {
    const base = emptyCreateCustomerForm();
    if (initialQuery) base.contact_name = initialQuery;
    return base;
  });
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [scanNotice, setScanNotice] = useState<{ text: string; isError: boolean } | null>(null);
  const [translating, setTranslating] = useState<
    Partial<Record<TranslatablePair | TranslatableFormField, boolean>>
  >({});

  // ── Collapsible sections ─────────────────────────────────────────────────
  // Expanded by default; purely manual — no auto-collapse.
  const [expanded, setExpanded] = useState<Record<SectionKey, boolean>>({
    identification: true,
    address: true,
  });

  // Which file-input invocation triggered the picker: the header button
  // scans everything, a section button scans but only applies that section.
  const scanTargetRef = useRef<SectionKey | "all">("all");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const translateTimers = useRef<
    Partial<Record<TranslatablePair | TranslatableFormField, ReturnType<typeof setTimeout>>>
  >({});

  const [touched, setTouched] = useState<{ vat: boolean; crn: boolean }>({ vat: false, crn: false });

  const isIdentificationComplete = (f: CreateCustomerForm) =>
    !!(f.contact_name.trim() && f.contact_name_sec_lang.trim() && f.tax_reg_no.trim() && f.buyer_id_value.trim());

  const isAddressComplete = (a: CustomerAddressForm) =>
    !!(
      a.building_number.trim() &&
      a.additional_number.trim() &&
      a.zip.trim() &&
      a.street.trim() &&
      a.district.trim() &&
      a.city.trim() &&
      a.state.trim() &&
      a.country.trim()
    );

  const toggleSection = (key: SectionKey) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  if (!isOpen) return null;

  const setField = (field: keyof CreateCustomerForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  // Editing the Arabic (primary) name debounce-translates into the English
  // (secondary) name field automatically — same pattern as the address
  // fields below; the English field stays independently editable afterwards.
  const setPrimaryName = (value: string) => {
    setForm((prev) => ({ ...prev, contact_name: value }));

    if (translateTimers.current.name) clearTimeout(translateTimers.current.name);
    if (!value.trim()) {
      setForm((prev) => ({ ...prev, contact_name_sec_lang: "" }));
      return;
    }

    translateTimers.current.name = setTimeout(async () => {
      setTranslating((prev) => ({ ...prev, name: true }));
      try {
        const res = await fetch(`${apiUrl}/customers/translate-field`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "x-password": password || "" },
          body: JSON.stringify({ field: "name", value }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const result = await res.json();
        if (result.ok && result.value) {
          setForm((prev) => ({ ...prev, contact_name_sec_lang: result.value }));
        }
      } catch (err) {
        console.error("Translation failed for name:", err);
      } finally {
        setTranslating((prev) => ({ ...prev, name: false }));
      }
    }, DEBOUNCE_MS);
  };

  // building_number / additional_number / zip are the same digits in both
  // languages — one input writes both the primary and _sec_lang Zoho fields.
  const setSharedAddressField = (field: SharedAddressField, value: string) => {
    setForm((prev) => ({
      ...prev,
      billing_address: { ...prev.billing_address, [field]: value },
    }));
  };

  // street/district/city/state/country: editing the Arabic (primary) value
  // debounce-translates into the English (secondary) field automatically;
  // the English field stays independently editable afterwards.
  const setPrimaryAddressField = (field: TranslatablePair, value: string) => {
    const secKey = `${field}_sec_lang` as keyof CustomerAddressForm;
    setForm((prev) => ({
      ...prev,
      billing_address: { ...prev.billing_address, [field]: value },
    }));

    if (translateTimers.current[field]) clearTimeout(translateTimers.current[field]);
    if (!value.trim()) {
      setForm((prev) => ({
        ...prev,
        billing_address: { ...prev.billing_address, [secKey]: "" },
      }));
      return;
    }

    translateTimers.current[field] = setTimeout(async () => {
      setTranslating((prev) => ({ ...prev, [field]: true }));
      try {
        const res = await fetch(`${apiUrl}/customers/translate-field`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "x-password": password || "" },
          body: JSON.stringify({ field, value }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const result = await res.json();
        if (result.ok && result.value) {
          setForm((prev) => ({
            ...prev,
            billing_address: { ...prev.billing_address, [secKey]: result.value },
          }));
        }
      } catch (err) {
        console.error(`Translation failed for ${field}:`, err);
      } finally {
        setTranslating((prev) => ({ ...prev, [field]: false }));
      }
    }, DEBOUNCE_MS);
  };

  const setSecondaryAddressField = (field: TranslatablePair, value: string) => {
    const secKey = `${field}_sec_lang` as keyof CustomerAddressForm;
    setForm((prev) => ({
      ...prev,
      billing_address: { ...prev.billing_address, [secKey]: value },
    }));
  };

  const resetAndClose = () => {
    setForm(emptyCreateCustomerForm());
    setSaveError(null);
    setScanNotice(null);
    setExpanded({ identification: true, address: true });
    setTouched({ vat: false, crn: false });
    onClose();
  };

  function openScanPicker(target: SectionKey | "all") {
    scanTargetRef.current = target;
    fileInputRef.current?.click();
  }

  async function handleScanFile(file: File) {
    const target = scanTargetRef.current;
    setScanning(true);
    setScanNotice(null);
    try {
      const body = new FormData();
      body.append("file", file);
      const res = await fetch(`${apiUrl}/customers/scan`, {
        method: "POST",
        headers: { "x-password": password || "" },
        body,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result = await res.json();
      if (!result.ok || !result.data) throw new Error("scan returned no data");

      const d = result.data;

      if (target === "all" || target === "identification") {
        setForm((prev) => ({
          ...prev,
          contact_name: d.contact_name || prev.contact_name,
          contact_name_sec_lang: d.contact_name_sec_lang || prev.contact_name_sec_lang,
          tax_reg_no: d.tax_reg_no || prev.tax_reg_no,
          buyer_id_value: d.buyer_id_value || prev.buyer_id_value,
        }));
        setExpanded((prev) => ({ ...prev, identification: true }));
      }

      if (target === "all" || target === "address") {
        setForm((prev) => ({
          ...prev,
          billing_address: {
            ...prev.billing_address,
            ...(d.billing_address ?? {}),
          },
        }));
        setExpanded((prev) => ({ ...prev, address: true }));
      }

      setScanNotice({ text: t.scanDocumentSuccess, isError: false });
    } catch (err) {
      console.error("Document scan failed:", err);
      setScanNotice({ text: t.scanDocumentError, isError: true });
    } finally {
      setScanning(false);
    }
  }

  function validate(): string | null {
    const { billing_address: a } = form;
    const requiredFilled = isIdentificationComplete(form) && isAddressComplete(a);
    if (!requiredFilled) return t.requiredFieldsMissing;
    if (!VAT_PATTERN.test(form.tax_reg_no.trim())) return t.vatInvalid;
    if (!CRN_PATTERN.test(form.buyer_id_value.trim())) return t.crnInvalid;
    return null;
  }

  async function handleSave() {
    setTouched({ vat: true, crn: true });
    const validationError = validate();
    if (validationError) {
      setSaveError(validationError);
      return;
    }
    setSaving(true);
    setSaveError(null);
    try {
      const res = await fetch(`${apiUrl}/customers`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-password": password || "" },
        body: JSON.stringify({
          contact_name: form.contact_name.trim(),
          contact_name_sec_lang: form.contact_name_sec_lang.trim(),
          tax_reg_no: form.tax_reg_no.trim(),
          buyer_id_value: form.buyer_id_value.trim(),
          billing_address: form.billing_address,
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data?.error?.message ?? "create failed");

      onCreated(data.contact as Customer);
      resetAndClose();
    } catch (err) {
      console.error("Error creating customer:", err);
      setSaveError(t.customerCreateError);
    } finally {
      setSaving(false);
    }
  }

  const address = form.billing_address;
  const vatError = touched.vat && form.tax_reg_no.trim() && !VAT_PATTERN.test(form.tax_reg_no.trim());
  const crnError = touched.crn && form.buyer_id_value.trim() && !CRN_PATTERN.test(form.buyer_id_value.trim());

  return (
    <div className="ccm-overlay" role="dialog" aria-modal="true" onClick={resetAndClose}>
      <div className="ccm-modal" onClick={(e) => e.stopPropagation()}>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,.pdf,application/pdf"
          className="ccm-file-input"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleScanFile(file);
            e.target.value = "";
          }}
        />

        <div className="ccm-header">
          <h2 className="ccm-title">{t.createCustomerTitle}</h2>
          <div className="ccm-header-actions">
            <button
              type="button"
              className="ccm-scan-btn ccm-scan-btn--header"
              disabled={scanning}
              onClick={() => openScanPicker("all")}
              title={t.scanDocumentBtn}
            >
              <Upload size={13} />
              {scanning ? t.scanningDocument : t.scanDocumentBtn}
            </button>
            <button type="button" className="ccm-close" onClick={resetAndClose} aria-label={t.modalCancel}>
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="ccm-body">
          {scanNotice && (
            <div className={`ccm-scan-notice ${scanNotice.isError ? "ccm-scan-notice--error" : ""}`}>
              {scanNotice.text}
            </div>
          )}

          <div className="ccm-section">
            <div className="ccm-section-header">
              <button
                type="button"
                className="ccm-section-toggle"
                onClick={() => toggleSection("identification")}
                aria-expanded={expanded.identification}
              >
                <ChevronDown
                  size={16}
                  className={`ccm-chevron ${expanded.identification ? "" : "ccm-chevron--collapsed"}`}
                />
                <h3 className="ccm-section-title">{t.identificationSection}</h3>
              </button>
              <button
                type="button"
                className="ccm-section-scan-btn"
                disabled={scanning}
                onClick={() => openScanPicker("identification")}
                aria-label={t.scanDocumentBtn}
                title={t.scanDocumentBtn}
              >
                <ScanLine size={14} />
              </button>
            </div>

            {expanded.identification && (
              <div className="ccm-grid ccm-grid--2">
                <label className="ccm-field">
                  <span>{t.fieldNameAr} * {translating.name && <em className="ccm-translating">…</em>}</span>
                  <input
                    type="text"
                    dir="rtl"
                    value={form.contact_name}
                    onChange={(e) => setPrimaryName(e.target.value)}
                  />
                </label>
                <label className="ccm-field">
                  <span>{t.fieldNameEn} *</span>
                  <input
                    type="text"
                    value={form.contact_name_sec_lang}
                    onChange={(e) => setField("contact_name_sec_lang", e.target.value)}
                  />
                </label>
                <label className="ccm-field">
                  <span>{t.fieldVat} *</span>
                  <input
                    type="text"
                    value={form.tax_reg_no}
                    onChange={(e) => setField("tax_reg_no", e.target.value)}
                    onBlur={() => setTouched((prev) => ({ ...prev, vat: true }))}
                    aria-invalid={!!vatError}
                  />
                  {vatError && <span className="ccm-field-error">{t.vatInvalid}</span>}
                </label>
                <label className="ccm-field">
                  <span>{t.fieldBuyerIdValue} *</span>
                  <input
                    type="text"
                    value={form.buyer_id_value}
                    onChange={(e) => setField("buyer_id_value", e.target.value)}
                    onBlur={() => setTouched((prev) => ({ ...prev, crn: true }))}
                    aria-invalid={!!crnError}
                  />
                  {crnError && <span className="ccm-field-error">{t.crnInvalid}</span>}
                </label>
              </div>
            )}
          </div>

          <div className="ccm-section">
            <div className="ccm-section-header">
              <button
                type="button"
                className="ccm-section-toggle"
                onClick={() => toggleSection("address")}
                aria-expanded={expanded.address}
              >
                <ChevronDown
                  size={16}
                  className={`ccm-chevron ${expanded.address ? "" : "ccm-chevron--collapsed"}`}
                />
                <h3 className="ccm-section-title">{t.addressSection}</h3>
              </button>
              <button
                type="button"
                className="ccm-section-scan-btn"
                disabled={scanning}
                onClick={() => openScanPicker("address")}
                aria-label={t.scanDocumentBtn}
                title={t.scanDocumentBtn}
              >
                <ScanLine size={14} />
              </button>
            </div>

            {expanded.address && (
              <>
                <div className="ccm-grid ccm-grid--3">
                  <label className="ccm-field">
                    <span>{t.fieldBuildingNumber} *</span>
                    <input
                      dir="rtl"
                      type="text"
                      value={address.building_number}
                      onChange={(e) => setSharedAddressField("building_number", e.target.value)}
                    />
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldAdditionalNumber} *</span>
                    <input
                      dir="rtl"
                      type="text"
                      value={address.additional_number}
                      onChange={(e) => setSharedAddressField("additional_number", e.target.value)}
                    />
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldPostalCode} *</span>
                    <input
                      dir="rtl"
                      type="text"
                      value={address.zip}
                      onChange={(e) => setSharedAddressField("zip", e.target.value)}
                    />
                  </label>
                </div>

                <h4 className="ccm-subsection-title">{t.primaryLangSection}</h4>
                <div className="ccm-grid ccm-grid--3">
                  <label className="ccm-field">
                    <span>{t.fieldStreet} * {translating.street && <em className="ccm-translating">…</em>}</span>
                    <input
                      dir="rtl"
                      type="text"
                      value={address.street}
                      onChange={(e) => setPrimaryAddressField("street", e.target.value)}
                    />
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldDistrict} * {translating.district && <em className="ccm-translating">…</em>}</span>
                    <input
                      dir="rtl"
                      type="text"
                      value={address.district}
                      onChange={(e) => setPrimaryAddressField("district", e.target.value)}
                    />
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldCity} *</span>
                    <select
                      dir="rtl"
                      value={address.city}
                      onChange={(e) => {
                        const match = SAUDI_CITIES.find((c) => c.ar === e.target.value);
                        setForm((prev) => ({
                          ...prev,
                          billing_address: {
                            ...prev.billing_address,
                            city: e.target.value,
                            city_sec_lang: match ? match.en : prev.billing_address.city_sec_lang,
                          },
                        }));
                      }}
                    >
                      {SAUDI_CITIES.map((c) => (
                        <option key={c.ar} value={c.ar}>{c.ar}</option>
                      ))}
                    </select>
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldState} *</span>
                    <select
                      dir="rtl"
                      value={address.state}
                      onChange={(e) => {
                        const match = SAUDI_STATES.find((s) => s.ar === e.target.value);
                        setForm((prev) => ({
                          ...prev,
                          billing_address: {
                            ...prev.billing_address,
                            state: e.target.value,
                            state_sec_lang: match ? match.en : prev.billing_address.state_sec_lang,
                          },
                        }));
                      }}
                    >
                      {SAUDI_STATES.map((s) => (
                        <option key={s.ar} value={s.ar}>{s.ar}</option>
                      ))}
                    </select>
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldCountry} *</span>
                    <select
                      dir="rtl"
                      value={address.country}
                      onChange={(e) => {
                        const match = COUNTRIES.find((c) => c.ar === e.target.value);
                        setForm((prev) => ({
                          ...prev,
                          billing_address: {
                            ...prev.billing_address,
                            country: e.target.value,
                            country_sec_lang: match ? match.en : prev.billing_address.country_sec_lang,
                          },
                        }));
                      }}
                    >
                      {COUNTRIES.map((c) => (
                        <option key={c.ar} value={c.ar}>{c.ar}</option>
                      ))}
                    </select>
                  </label>
                </div>

                <h4 className="ccm-subsection-title">{t.secondaryLangSection}</h4>
                <div className="ccm-grid ccm-grid--3">
                  <label className="ccm-field">
                    <span>{t.fieldStreet}</span>
                    <input
                      type="text"
                      value={address.street_sec_lang}
                      onChange={(e) => setSecondaryAddressField("street", e.target.value)}
                    />
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldDistrict}</span>
                    <input
                      type="text"
                      value={address.district_sec_lang}
                      onChange={(e) => setSecondaryAddressField("district", e.target.value)}
                    />
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldCity}</span>
                    <input
                      type="text"
                      value={address.city_sec_lang}
                      onChange={(e) => setSecondaryAddressField("city", e.target.value)}
                    />
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldState}</span>
                    <input
                      type="text"
                      value={address.state_sec_lang}
                      onChange={(e) => setSecondaryAddressField("state", e.target.value)}
                    />
                  </label>
                  <label className="ccm-field">
                    <span>{t.fieldCountry}</span>
                    <input
                      type="text"
                      value={address.country_sec_lang}
                      onChange={(e) => setSecondaryAddressField("country", e.target.value)}
                    />
                  </label>
                </div>
              </>
            )}
          </div>

          {saveError && <div className="ccm-save-error">{saveError}</div>}
        </div>

        <div className="ccm-footer">
          <button type="button" className="ccm-cancel-btn" onClick={resetAndClose} disabled={saving}>
            {t.modalCancel}
          </button>
          <button type="button" className="ccm-save-btn" onClick={handleSave} disabled={saving}>
            {saving ? t.modalSaving : t.modalSave}
          </button>
        </div>
      </div>
    </div>
  );
}
