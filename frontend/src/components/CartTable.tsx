import "../styles/CartTable.css";
import { useCart } from "../context/CartContext";
import { Trash2, Check, Printer } from "lucide-react";
import { useLocale } from "../context/LangContext";
import { useState, useEffect } from "react";
import InputSearch from "./InputSearch";
import { PaymentMethodModal } from "./PaymentMethodModal";
import { usePassword } from "../context/PasswordContext";
import { apiUrl } from "../env";
import { printPdf } from "../utils/printPdf";
import type { Item } from "../types";
import type { NoticeState } from "../App";

type PaymentMethod = "Cash" | "Credit Card";
type PendingAction = "submit" | "print" | null;

interface RawInputs {
  qty: string;
  rate: string;
}

interface CartTableProps {
  items: Item[];
  itemsLoading: boolean;
  itemsError: boolean;
  onNotice: (notice: NoticeState) => void;
}

export default function CartTable({ items, itemsLoading, itemsError, onNotice }: CartTableProps) {
  const [paymentModal, setPaymentModal] = useState(false);
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const { password } = usePassword();
  const { cart, setCart, removeFromCart } = useCart();
  const { t } = useLocale();
  const [isLoading, setIsLoading] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
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

  // ── Input handlers ───────────────────────────────────────────────────────
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

  // ── Validation ───────────────────────────────────────────────────────────
  function runValidation(): boolean {
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

  // ── Invoice helpers ──────────────────────────────────────────────────────
  const buildPayload = () => cart.map(({ item_id, rate, qty }) => ({ item_id, rate, quantity: qty }));

  async function submitInvoice(method: PaymentMethod): Promise<{
    invoice_id: string;
    invoice_number: string;
  }> {
    const response = await fetch(`${apiUrl}/invoices/walk-in?method=${method}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-password": password || "" },
      body: JSON.stringify(buildPayload()),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async function createInvoice(method: PaymentMethod) {
    setIsLoading(true);
    try {
      const data = await submitInvoice(method);
      resetCart();
      onNotice({ message: t.noticeSubmitted, invoiceId: data.invoice_id });
    } catch (err) {
      console.error("Error creating invoice:", err);
    } finally {
      setIsLoading(false);
    }
  }

  async function createInvoiceNPrint(method: PaymentMethod) {
    setIsLoading(true);
    try {
      const data = await submitInvoice(method);
      resetCart();
      onNotice({ message: t.noticeSubmittedAndPrinted, invoiceId: data.invoice_id });
      await printPdf(`${apiUrl}/invoice/${data.invoice_id}/pdf`, { "x-password": password || "" });
    } catch (err) {
      console.error("Error creating/printing invoice:", err);
    } finally {
      setIsLoading(false);
    }
  }

  // ── Submit entry points ──────────────────────────────────────────────────
  function handleSubmitClick() {
    if (!runValidation()) return;
    setPendingAction("submit");
    setPaymentModal(true);
  }
  function handlePrintClick() {
    if (!runValidation()) return;
    setPendingAction("print");
    setPaymentModal(true);
  }
  function handlePaymentSelect(method: PaymentMethod) {
    setPaymentModal(false);
    if (pendingAction === "print") {
      createInvoiceNPrint(method);
    } else if (pendingAction === "submit") {
      createInvoice(method);
    }
    setPendingAction(null);
  }

  // ── Totals ───────────────────────────────────────────────────────────────
  const total = cart.reduce((sum, e) => sum + e.rate * e.qty, 0);
  const subtotal = total / 1.15;
  const taxAmount = total - subtotal;
  const fmt = (n: number) => n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  const cartEmpty = cart.length === 0;

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <div className="pos-tab-body">
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
            <button
              type="button"
              className="btn-primary"
              disabled={isLoading || cartEmpty}
              onClick={handleSubmitClick}
            >
              <Check size={15} />
              {t.submitOrder}
            </button>
            <button
              type="button"
              className="btn-secondary"
              disabled={isLoading || cartEmpty}
              onClick={handlePrintClick}
            >
              <Printer size={15} />
              {t.submitNPrintOrder}
            </button>
          </div>
        </div>
      </div>

      <PaymentMethodModal
        isOpen={paymentModal}
        onClose={() => {
          setPaymentModal(false);
          setPendingAction(null);
        }}
        onSelect={handlePaymentSelect}
      />
    </div>
  );
}
