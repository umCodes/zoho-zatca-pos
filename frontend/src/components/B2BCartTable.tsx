import "../styles/CartTable.css";
import { useCart } from "../context/CartContext";
import { Trash2, Check } from "lucide-react";
import { useLocale } from "../context/LangContext";
import { useState, useEffect } from "react";
import InputSearch from "./InputSearch";
import CustomerSearch from "./CustomerSearch";
import { usePassword } from "../context/PasswordContext";
import { apiUrl } from "../env";
import type { Customer, Item } from "../types";
import type { NoticeState } from "../App";

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

interface DraftInvoice {
  invoice_id: string;
  invoice_number: string;
  amount: number;
  sent: boolean;
}

export default function B2BCartTable({ items, itemsLoading, itemsError, onNotice }: B2BCartTableProps) {
  const { password } = usePassword();
  const { cart, setCart, removeFromCart } = useCart();
  const { t } = useLocale();

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [draft, setDraft] = useState<DraftInvoice | null>(null);
  const [rawInputs, setRawInputs] = useState<Record<string, RawInputs>>({});

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
    setValidationError(null);
    return true;
  }

  const buildPayload = () => cart.map(({ item_id, rate, qty }) => ({ item_id, rate, quantity: qty }));

  async function createDraft() {
    if (!runValidation() || !customer) return;
    setIsCreating(true);
    try {
      const response = await fetch(
        `${apiUrl}/invoices/b2b?customer_id=${encodeURIComponent(customer.contact_id)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", "x-password": password || "" },
          body: JSON.stringify(buildPayload()),
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setDraft({
        invoice_id: data.invoice_id,
        invoice_number: data.invoice_number,
        amount: data.amount,
        sent: false,
      });
      resetCart();
      onNotice({ message: t.noticeDraftCreated });
    } catch (err) {
      console.error("Error creating B2B draft invoice:", err);
      setValidationError(t.customerCreateError);
    } finally {
      setIsCreating(false);
    }
  }

  async function sendDraft() {
    if (!draft) return;
    setIsSending(true);
    try {
      const response = await fetch(`${apiUrl}/invoices/${draft.invoice_id}/send`, {
        method: "POST",
        headers: { "x-password": password || "" },
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setDraft((prev) => (prev ? { ...prev, sent: true } : prev));
      onNotice({ message: t.noticeInvoiceSent, invoiceId: draft.invoice_id });
    } catch (err) {
      console.error("Error sending B2B invoice:", err);
    } finally {
      setIsSending(false);
    }
  }

  function startNewInvoice() {
    setDraft(null);
    setCustomer(null);
  }

  const total = cart.reduce((sum, e) => sum + e.rate * e.qty, 0);
  const subtotal = total / 1.15;
  const taxAmount = total - subtotal;
  const fmt = (n: number) => n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  const isBusy = isCreating || isSending;
  const cartEmpty = cart.length === 0;
  const submitDisabled = isCreating || cartEmpty || !customer;

  return (
    <div className="pos-tab-body">
      <div className="pos-search-row pos-search-row--b2b">
        <CustomerSearch selected={customer} onSelect={setCustomer} onClear={() => setCustomer(null)} />
      </div>

      {draft ? (
        <div className="draft-panel">
          <div className="draft-panel__row">
            <span className="draft-panel__label">{t.draftInvoiceCreated}</span>
            <span className="draft-panel__value">#{draft.invoice_number}</span>
          </div>
          <div className="draft-panel__row">
            <span className="draft-panel__label">{t.total}</span>
            <span className="draft-panel__value">{t.currency} {fmt(draft.amount)}</span>
          </div>
          <div className="draft-panel__row">
            <span className={`status-badge ${draft.sent ? "status-badge--sent" : "status-badge--draft"}`}>
              {draft.sent ? t.invoiceStatusSent : t.invoiceStatusDraft}
            </span>
          </div>
          <div className="draft-panel__actions">
            {!draft.sent && (
              <button type="button" className="btn-primary" disabled={isBusy} onClick={sendDraft}>
                <Check size={15} />
                {isSending ? t.sendingInvoice : t.sendInvoice}
              </button>
            )}
            <button type="button" className="btn-secondary" disabled={isBusy} onClick={startNewInvoice}>
              {t.newInvoice}
            </button>
          </div>
        </div>
      ) : (
        <>
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
                      return (
                        <tr key={entry.line_id} className={isInvalidRow ? "row--invalid" : ""}>
                          <td className="col-item">
                            <span className="item-sku">{entry.sku}</span>
                            <span className="item-name">{entry.name}</span>
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
                <button type="button" className="btn-primary" disabled={submitDisabled} onClick={createDraft}>
                  <Check size={15} />
                  {isCreating ? t.creatingDraftInvoice : t.createDraftInvoice}
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
