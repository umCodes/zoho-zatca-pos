import "../styles/CartTable.css";
import { useCart } from "../context/CartContext";
import { FaTrash, FaMoneyBillWave, FaCreditCard } from "react-icons/fa";
import { useLocale } from "../context/LangContext";
import { useState, useEffect } from "react";
import SpinnerButton from "./SpinnerButton";
import AlertModal from "./AlertModal";
import { usePassword } from "../context/PasswordContext";
import { apiUrl } from "../env";

// ── Types ─────────────────────────────────────────────────────────────────────

type PaymentMethod = "Cash" | "Credit Card";

interface RawInputs {
  qty: string;
  rate: string;
}

interface CartTableProps {
  title?: string;
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function CartTable({ title = "Order Summary" }: CartTableProps) {
  const { password } = usePassword()
  const { cart, setCart, removeFromCart } = useCart();
  const { t } = useLocale();

  const [isLoading, setIsLoading] = useState(false);
  const [payment, setPayment] = useState<PaymentMethod>("Cash");
  const [validationError, setValidationError] = useState<string | null>(null);

  // ── Alert modal state ────────────────────────────────────────────────────
  const [alertOpen, setAlertOpen] = useState(false);
  const [invoiceResult, setInvoiceResult] = useState<{
    invoice_id: string;
    invoice_number: string;
  } | null>(null);

  const [rawInputs, setRawInputs] = useState<Record<string, RawInputs>>({});

  const resetCart = () => {
    setCart([]);
    setRawInputs({});
    setValidationError(null);
  };

  useEffect(() => {
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
      setCart((prev) =>
        prev.map((entry) =>
          entry.line_id === id ? { ...entry, [field]: n } : entry
        )
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
  const buildPayload = () =>
    cart.map(({ item_id, rate, qty }) => ({ item_id, rate, quantity: qty }));
  

  async function submitInvoice(): Promise<{
    invoice_id: string;
    invoice_number: string;
  }> {
    const response = await fetch(
      `${apiUrl}/invoices/walk-in?method=${payment}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json","x-password": password || "" },
        body: JSON.stringify(buildPayload()),
      }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  /** Opens the PDF for the last submitted invoice in a new tab. */
  const handlePrintInvoice = () => {
    if (!invoiceResult) return;
    window.open(
      `${apiUrl}/invoice/${invoiceResult.invoice_id}/pdf`,
      "_blank"
    );
    setAlertOpen(false);
  };

  const handleAlertOk = () => {
    setAlertOpen(false);
    setInvoiceResult(null);
  };

  async function createInvoice() {
    if (!runValidation()) return;
    setIsLoading(true);
    try {
      const data = await submitInvoice();
      resetCart();
      setInvoiceResult(data);
      setAlertOpen(true);
    } catch (err) {
      console.error("Error creating invoice:", err);
    } finally {
      setIsLoading(false);
    }
  }

  async function createInvoiceNPrint() {
    if (!runValidation()) return;
    setIsLoading(true);
    try {
      const data = await submitInvoice();
      resetCart();
      setInvoiceResult(data);
      setAlertOpen(true);
      // Auto-open PDF immediately, modal still shows for a second print if needed
      window.open(
        `http://127.0.0.1:8000/invoice/${data.invoice_id}/pdf`,
        "_blank"
      );
    } catch (err) {
      console.error("Error creating/printing invoice:", err);
    } finally {
      setIsLoading(false);
    }
  }

  // ── Totals ───────────────────────────────────────────────────────────────
  const total = cart.reduce((sum, e) => sum + e.rate * e.qty, 0);
  const subtotal = total / 1.15;
  const taxAmount = total - subtotal;

  const fmt = (n: number) =>
    n.toLocaleString("en-US", { style: "currency", currency: t.currency });

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <div className="cart-root">
      {isLoading && (
        <div className="overlay">
          <div className="overlay-content">
            <span className="overlay-spinner" />
            <p className="overlay-message">{t.processingOrder}</p>
          </div>
        </div>
      )}

      <p className="cart-title">{title}</p>

      {/* ── Items table ── */}
      <div className="table-wrapper">
        <table className="cart-table">
          <thead>
            <tr>
              <th>{t.itemName}</th>
              <th>{t.quantity}</th>
              <th>{t.price}</th>
              <th>{t.total}</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {cart.map((entry) => {
              const raw = rawInputs[entry.line_id];
              const parsedQty = parseFloat(raw?.qty ?? "");
              const isInvalidRow =
                !!validationError && (isNaN(parsedQty) || parsedQty < 1);
              const lineTotal = entry.rate * entry.qty;

              return (
                <tr
                  key={entry.line_id}
                  className={isInvalidRow ? "row--invalid" : ""}
                >
                  <td>
                    <span className="item-status" aria-label={entry.status} />
                    <span className="item-name">{entry.name}</span>
                    <span className="item-description">{entry.description}</span>
                    <span className="item-tax">{t.vatPercent}</span>
                  </td>

                  <td>
                    <input
                      className={`cell-input cell-input--qty${isInvalidRow ? " cell-input--error" : ""}`}
                      type="number"
                      min={0.01}
                      value={raw?.qty ?? String(entry.qty)}
                      onChange={(e) =>
                        handleChange(entry.line_id, "qty", e.target.value)
                      }
                      aria-label={t.ariaQuantity}
                      aria-invalid={isInvalidRow}
                    />
                    <span className="cell-input-suffix">{entry.unit}</span>
                  </td>

                  <td className="cell-price">
                    <div className="cell-price-wrap">
                      <span className="cell-input-prefix">{t.currency}</span>
                      <input
                        className="cell-input cell-input--price"
                        type="number"
                        min={0}
                        step={0.01}
                        value={raw?.rate ?? String(entry.rate)}
                        onChange={(e) =>
                          handleChange(entry.line_id, "rate", e.target.value)
                        }
                        aria-label={t.ariaUnitPrice}
                      />
                      <span className="cell-input-suffix">
                        {t.per} {entry.unit}
                      </span>
                    </div>
                  </td>

                  <td className="cell-total">{fmt(lineTotal)}</td>

                  <td>
                    <button
                      className="remove-btn"
                      onClick={() => removeFromCart(entry.line_id)}
                      aria-label={t.ariaRemoveItem(entry.name)}
                    >
                      <FaTrash size={20} color="red" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* ── Footer ── */}
      <div className="cart-footer">
        <div className="cart-summary">
          <div className="summary-row">
            <span>{t.subtotal}</span>
            <span>{fmt(subtotal)}</span>
          </div>
          <div className="summary-row">
            <span>{t.vatPercent}</span>
            <span>{fmt(taxAmount)}</span>
          </div>
          <div className="summary-grand">
            <span>{t.grandTotal}</span>
            <span>{fmt(total)}</span>
          </div>

          <div
            className="payment-toggle"
            role="group"
            aria-label={t.ariaPaymentMethod}
          >
            <button
              type="button"
              className={`payment-option${payment === "Cash" ? " payment-option--active" : ""}`}
              onClick={() => setPayment("Cash")}
              aria-pressed={payment === "Cash"}
            >
              <FaMoneyBillWave size={16} />
              <span>{t.cash}</span>
            </button>
            <button
              type="button"
              className={`payment-option${payment === "Credit Card" ? " payment-option--active" : ""}`}
              onClick={() => setPayment("Credit Card")}
              aria-pressed={payment === "Credit Card"}
            >
              <FaCreditCard size={16} />
              <span>{t.card}</span>
            </button>
          </div>

          {validationError && (
            <div className="validation-error" role="alert">
              <span className="validation-error__icon">!</span>
              <span>{validationError}</span>
            </div>
          )}

          <div className="submit-root">
            <SpinnerButton
              className="submit-n-print-btn"
              disabled={isLoading}
              onClick={createInvoiceNPrint}
              loadingLabel={t.submitNPrintOrder}
              label={t.submitNPrintOrder}
            />
            <SpinnerButton
              className="submit-btn"
              disabled={isLoading}
              onClick={createInvoice}
              loadingLabel={t.submitOrder}
              label={t.submitOrder}
            />
          </div>
        </div>
      </div>

      {/* ── Alert modal ── */}
      <AlertModal
        isOpen={alertOpen}
        title={t.invoiceCreated ?? "Invoice Created"}
        message={
          invoiceResult
            ? `${t.invoiceCreated ?? "Invoice"} #${invoiceResult.invoice_number}`
            : undefined
        }
        okLabel={t.ok ?? "OK"}
        customLabel={t.print ?? "Print"}
        onOk={handleAlertOk}
        onCustom={handlePrintInvoice}
        onOverlayClick={handleAlertOk}
      />
    </div>
  );
}