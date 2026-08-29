import "../styles/CartTable.css";
import { useCart } from "../context/CartContext";
import { Trash2, Check, Printer } from "lucide-react";
import { useLocale } from "../context/LangContext";
import { useState, useEffect } from "react";
import InputSearch from "./InputSearch";
import CustomerSearch from "./CustomerSearch";
import ConfirmInvoiceModal from "./ConfirmInvoiceModal";
import { usePassword } from "../context/PasswordContext";
import { apiUrl } from "../env";
import type { Customer, CustomerDetail, Item } from "../types";
import type { NoticeState } from "../App";
import { validateCustomerForB2B, type CustomerIssue } from "../utils/customerValidation";
import { validateLineItem, type LineItemIssue } from "../utils/lineItemValidation";
import { printPdf } from "../utils/printPdf";
import { getCached, setCached } from "../utils/apiCache";

// Mirrors the backend's own customer cache TTL (contacts.py) — matches
// CustomerSearch's search-result cache for the same reason.
const CUSTOMER_DETAIL_CACHE_TTL_MS = 60 * 1000;
// Item catalog/detail changes rarely — same TTL as the item list cache in App.tsx.
const ITEM_DETAIL_CACHE_TTL_MS = 5 * 60 * 1000;

interface RawInputs {
  qty: string;
  rate: string;
}

interface B2BCartTableProps {
  items: Item[];
  itemsLoading: boolean;
  itemsError: boolean;
  onNotice: (notice: NoticeState) => void;
}

export default function B2BCartTable({ items, itemsLoading, itemsError, onNotice }: B2BCartTableProps) {
  const { password } = usePassword();
  const { cart, setCart, removeFromCart } = useCart();
  const { t } = useLocale();

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [customerDetailLoading, setCustomerDetailLoading] = useState(false);
  const [customerIssues, setCustomerIssues] = useState<CustomerIssue[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [rawInputs, setRawInputs] = useState<Record<string, RawInputs>>({});
  const [confirmIntent, setConfirmIntent] = useState<"save" | "print" | null>(null);
  // The /items list endpoint doesn't return name_sec_lang (Zoho only exposes
  // it via per-item detail) — fetched lazily per item_id as items enter the
  // cart, for ZATCA bilingual-name line-item validation.
  const [itemDetails, setItemDetails] = useState<Record<string, { name_sec_lang: string }>>({});

  const resetCart = () => {
    setCart([]);
    setRawInputs({});
    setValidationError(null);
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setRawInputs((prev) => {
      const next: Record<string, RawInputs> = {};
      for (const entry of cart) {
        next[entry.line_id] = prev[entry.line_id] ?? {
          qty: String(entry.qty),
          rate: String(entry.rate),
        };
      }
      return next;
    });
  }, [cart]);

  // Fetch full customer detail (address, VAT, CRN) as soon as a customer is
  // selected, and validate it against ZATCA Standard Tax Invoice
  // requirements automatically — no separate "check" action needed.
  useEffect(() => {
    if (!customer) {
      setCustomerIssues([]);
      return;
    }
    const cacheKey = `customer-detail:${customer.contact_id}`;
    const cached = getCached<CustomerDetail>(cacheKey);
    if (cached) {
      setCustomerIssues(validateCustomerForB2B(cached));
      return;
    }

    let cancelled = false;
    setCustomerDetailLoading(true);
    (async () => {
      try {
        const res = await fetch(`${apiUrl}/customers/${encodeURIComponent(customer.contact_id)}`, {
          headers: { "x-password": password || "" },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (cancelled) return;
        if (data.ok && data.customer) {
          setCached(cacheKey, data.customer as CustomerDetail, CUSTOMER_DETAIL_CACHE_TTL_MS);
          setCustomerIssues(validateCustomerForB2B(data.customer as CustomerDetail));
        } else {
          setCustomerIssues(["missingAddress", "missingVat", "missingCrn"]);
        }
      } catch (err) {
        console.error("Error fetching customer detail:", err);
        if (!cancelled) {
          setCustomerIssues(["missingAddress", "missingVat", "missingCrn"]);
        }
      } finally {
        if (!cancelled) setCustomerDetailLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [customer, password]);

  // Fetch each cart item's detail (for name_sec_lang) once, the first time
  // it appears in the cart — cached by item_id so repeated qty/rate edits
  // don't refetch.
  useEffect(() => {
    const missing = [...new Set(cart.map((e) => e.item_id))].filter((id) => !(id in itemDetails));
    if (missing.length === 0) return;
    let cancelled = false;
    (async () => {
      for (const itemId of missing) {
        const cacheKey = `item-detail:${itemId}`;
        const cached = getCached<{ name_sec_lang: string }>(cacheKey);
        if (cached) {
          setItemDetails((prev) => ({ ...prev, [itemId]: cached }));
          continue;
        }
        try {
          const res = await fetch(`${apiUrl}/items/${encodeURIComponent(itemId)}`, {
            headers: { "x-password": password || "" },
          });
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const data = await res.json();
          if (cancelled) return;
          const detail = { name_sec_lang: data.name_sec_lang || "" };
          setCached(cacheKey, detail, ITEM_DETAIL_CACHE_TTL_MS);
          setItemDetails((prev) => ({ ...prev, [itemId]: detail }));
        } catch (err) {
          console.error(`Error fetching item detail for ${itemId}:`, err);
          if (!cancelled) setItemDetails((prev) => ({ ...prev, [itemId]: { name_sec_lang: "" } }));
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [cart, itemDetails, password]);

  const handleChange = (id: string, field: keyof RawInputs, raw: string) => {
    setRawInputs((prev) => ({
      ...prev,
      [id]: { ...prev[id], [field]: raw },
    }));
    const n = parseFloat(raw);
    if (!isNaN(n)) {
      // Spec §6: setting quantity to 0 removes the line automatically.
      if (field === "qty" && n === 0) {
        removeFromCart(id);
        return;
      }
      setCart((prev) =>
        prev.map((entry) => (entry.line_id === id ? { ...entry, [field]: n } : entry))
      );
    }
  };

  const itemDetailsLoading = cart.some((e) => !(e.item_id in itemDetails));
  const lineItemIssues: Record<string, LineItemIssue[]> = {};
  for (const entry of cart) {
    const detail = itemDetails[entry.item_id];
    if (!detail) continue; // not fetched yet — don't flag prematurely
    const issues = validateLineItem({ ...entry, name_sec_lang: detail.name_sec_lang });
    if (issues.length > 0) lineItemIssues[entry.line_id] = issues;
  }
  const hasLineItemIssues = Object.keys(lineItemIssues).length > 0;

  function runValidation(): boolean {
    if (!customer) {
      setValidationError(t.validationNoCustomer);
      return false;
    }
    if (cart.length === 0) {
      setValidationError(t.validationEmptyCart);
      return false;
    }
    const invalidLines = cart.filter((entry) => {
      const qty = parseFloat(rawInputs[entry.line_id]?.qty ?? "");
      return isNaN(qty) || qty < 0.01;
    });
    if (invalidLines.length > 0) {
      const names = invalidLines.map((l) => l.name).join(", ");
      setValidationError(t.validationInvalidQty(names));
      return false;
    }
    if (customerIssues.length > 0) {
      setValidationError(t.validationCustomerIncomplete);
      return false;
    }
    if (hasLineItemIssues) {
      setValidationError(t.validationLineItemsIncomplete);
      return false;
    }
    setValidationError(null);
    return true;
  }

  const buildPayload = () => cart.map(({ item_id, rate, qty }) => ({ item_id, rate, quantity: qty }));

  function requestConfirm(intent: "save" | "print") {
    if (!runValidation()) return;
    setConfirmIntent(intent);
  }

  async function handleConfirmed() {
    if (!customer) return;
    setIsCreating(true);
    try {
      const response = await fetch(
        `${apiUrl}/invoices/b2b/confirm?customer_id=${encodeURIComponent(customer.contact_id)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", "x-password": password || "" },
          body: JSON.stringify(buildPayload()),
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const intent = confirmIntent;
      resetCart();
      setCustomer(null);
      setConfirmIntent(null);
      onNotice({ message: t.noticeInvoiceCreated, invoiceId: data.invoice_id });
      if (intent === "print") {
        await printPdf(`${apiUrl}/invoice/${data.invoice_id}/pdf`, { "x-password": password || "" });
      }
    } catch (err) {
      console.error("Error creating B2B invoice:", err);
      setValidationError(t.customerCreateError);
      setConfirmIntent(null);
    } finally {
      setIsCreating(false);
    }
  }

  const total = cart.reduce((sum, e) => sum + e.rate * e.qty, 0);
  const subtotal = total / 1.15;
  const taxAmount = total - subtotal;
  const fmt = (n: number) => n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  const cartEmpty = cart.length === 0;
  const submitDisabled =
    isCreating ||
    cartEmpty ||
    !customer ||
    customerDetailLoading ||
    customerIssues.length > 0 ||
    itemDetailsLoading ||
    hasLineItemIssues;

  const customerIssueLabel = (issue: CustomerIssue): string => {
    switch (issue) {
      case "notVatRegistered":
        return t.customerIssueNotVatRegistered;
      case "missingVat":
        return t.customerIssueMissingVat;
      case "missingCrn":
        return t.customerIssueMissingCrn;
      case "missingAddress":
        return t.customerIssueMissingAddress;
    }
  };

  const lineItemIssueLabel = (issue: LineItemIssue): string => {
    switch (issue) {
      case "missingRate":
        return t.lineItemIssueMissingRate;
      case "missingNameEn":
        return t.lineItemIssueMissingNameEn;
      case "missingNameAr":
        return t.lineItemIssueMissingNameAr;
      case "missingDescription":
        return t.lineItemIssueMissingDescription;
    }
  };

  return (
    <div className="pos-tab-body">
      <div className="pos-search-row pos-search-row--b2b">
        <CustomerSearch
          selected={customer}
          onSelect={setCustomer}
          onClear={() => setCustomer(null)}
          completeness={customer ? (customerDetailLoading ? "loading" : customerIssues.length === 0 ? "complete" : "incomplete") : undefined}
          issues={customerIssues}
          issueLabel={customerIssueLabel}
        />
      </div>

      <div className="pos-search-row">
        <InputSearch options={items} loading={itemsLoading} error={itemsError} />
      </div>

      <div className="cart-row">
        <div className="table-wrapper">
          <table className="cart-table">
            <thead>
              <tr>
                <th className="col-item">{t.itemName}</th>
                <th className="col-unit">{t.unitCol}</th>
                <th className="col-price">{t.priceCol}</th>
                <th className="col-qty">{t.quantity}</th>
                <th className="col-total">{t.lineTotalCol}</th>
                <th className="col-remove" />
              </tr>
            </thead>
            <tbody>
              {cartEmpty ? (
                <tr>
                  <td className="empty-state" colSpan={6}>
                    {t.emptyCartMessage}
                  </td>
                </tr>
              ) : (
                cart.map((entry) => {
                  const raw = rawInputs[entry.line_id];
                  const parsedQty = parseFloat(raw?.qty ?? "");
                  const isInvalidRow = !!validationError && (isNaN(parsedQty) || parsedQty < 1);
                  const lineTotal = entry.rate * entry.qty;
                  const issues = lineItemIssues[entry.line_id];
                  return (
                    <tr key={entry.line_id} className={isInvalidRow ? "row--invalid" : ""}>
                      <td className="col-item">
                        <span className="item-sku">{entry.sku}</span>
                        <span className="item-name">{entry.name}</span>
                        {issues && issues.length > 0 && (
                          <div className="line-item-issues">
                            {issues.map(lineItemIssueLabel).join(" · ")}
                          </div>
                        )}
                      </td>
                      <td className="col-unit">{entry.unit}</td>
                      <td className="col-price">
                        <input
                          className="cell-input cell-input--price"
                          type="number"
                          step="0.01"
                          min={0}
                          value={raw?.rate ?? String(entry.rate)}
                          onChange={(e) => handleChange(entry.line_id, "rate", e.target.value)}
                          aria-label={t.ariaUnitPrice}
                        />
                      </td>
                      <td className="col-qty">
                        <input
                          className={`cell-input cell-input--qty${isInvalidRow ? " cell-input--error" : ""}`}
                          type="number"
                          min={0}
                          value={raw?.qty ?? String(entry.qty)}
                          onChange={(e) => handleChange(entry.line_id, "qty", e.target.value)}
                          aria-label={t.ariaQuantity}
                          aria-invalid={isInvalidRow}
                        />
                      </td>
                      <td className="col-total cell-total">{fmt(lineTotal)}</td>
                      <td className="col-remove">
                        <button
                          className="remove-btn"
                          onClick={() => removeFromCart(entry.line_id)}
                          aria-label={t.ariaRemoveItem(entry.name)}
                        >
                          <Trash2 size={15} />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        <div className="checkout-panel">
          <div className="totals-block">
            <div className="totals-row">
              <span>{t.subtotal}</span>
              <span>{fmt(subtotal)}</span>
            </div>
            <div className="totals-row">
              <span>{t.vatPercent}</span>
              <span>{fmt(taxAmount)}</span>
            </div>
            <div className="totals-row totals-row--grand">
              <span>{t.grandTotal}</span>
              <span>{fmt(total)}</span>
            </div>
          </div>

          <div className="actions-row">
            {validationError && <span className="validation-text">{validationError}</span>}
            <button type="button" className="btn-secondary" disabled={submitDisabled} onClick={() => requestConfirm("save")}>
              <Check size={15} />
              {isCreating && confirmIntent === "save" ? t.creatingConfirmedInvoice : t.confirmInvoiceBtn}
            </button>
            <button type="button" className="btn-primary" disabled={submitDisabled} onClick={() => requestConfirm("print")}>
              <Printer size={15} />
              {isCreating && confirmIntent === "print" ? t.creatingConfirmedInvoice : t.confirmAndPrintInvoiceBtn}
            </button>
          </div>
        </div>
      </div>

      <ConfirmInvoiceModal
        isOpen={confirmIntent !== null}
        onCancel={() => setConfirmIntent(null)}
        onConfirm={handleConfirmed}
      />
    </div>
  );
}
