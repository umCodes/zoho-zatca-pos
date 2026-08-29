import { useEffect, useState } from "react";
import { Printer, Loader2 } from "lucide-react";
import "../styles/RecentInvoices.css";
import { useLocale } from "../context/LangContext";
import { usePassword } from "../context/PasswordContext";
import { apiUrl } from "../env";
import { printPdf } from "../utils/printPdf";

interface InvoiceRow {
  invoice_id: string;
  invoice_number: string;
  date: string;
  customer_id: string;
  customer_name: string;
  total: number;
  status: string;
  type: "walk-in" | "b2b";
}

interface TodaysInvoicesResponse {
  ok: boolean;
  date: string;
  count: number;
  total_amount: number;
  invoices: InvoiceRow[];
}

// Zoho statuses aren't a fixed set we fully control (draft, sent, paid,
// partially_paid, overdue, void, ...) — map the ones we expect onto the
// existing badge tones (shared with the B2B draft panel), and fall back to
// a neutral badge with the raw label for anything else.
function statusTone(status: string): "paid" | "sent" | "draft" | "neutral" {
  if (status === "paid" || status === "partially_paid") return "paid";
  if (status === "sent") return "sent";
  if (status === "draft") return "draft";
  return "neutral";
}

function formatStatusLabel(status: string): string {
  return status
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export default function RecentInvoices() {
  const { t } = useLocale();
  const { password } = usePassword();

  const [data, setData] = useState<TodaysInvoicesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [printingId, setPrintingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    fetch(`${apiUrl}/invoices/today`, { headers: { "x-password": password || "" } })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((result: TodaysInvoicesResponse) => {
        if (cancelled) return;
        if (!result.ok) throw new Error("request failed");
        setData(result);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [password]);

  const fmt = (n: number) =>
    n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  const handlePrint = async (invoiceId: string) => {
    setPrintingId(invoiceId);
    try {
      await printPdf(`${apiUrl}/invoice/${invoiceId}/pdf`, { "x-password": password || "" });
    } catch (err) {
      console.error("Failed to print invoice:", err);
    } finally {
      setPrintingId(null);
    }
  };

  return (
    <div className="pos-tab-body">
      <div className="invoices-summary-bar">
        <span className="invoices-summary-bar__count">
          {loading ? t.loadingInvoices : t.todaysInvoicesCount(data?.count ?? 0)}
        </span>
        {!loading && !error && (
          <span className="invoices-summary-bar__total">
            {t.todaysInvoicesTotal}: <strong>{fmt(data?.total_amount ?? 0)}</strong>
          </span>
        )}
      </div>

      <div className="table-wrapper">
        <table className="invoices-table">
          <thead>
            <tr>
              <th className="col-invnum">{t.invoiceNumberCol}</th>
              <th className="col-date">{t.dateCol}</th>
              <th className="col-type">{t.typeCol}</th>
              <th className="col-customer">{t.customerCol}</th>
              <th className="col-invtotal">{t.grandTotal}</th>
              <th className="col-status">{t.statusCol}</th>
              <th className="col-print" />
            </tr>
          </thead>
          <tbody>
            {error && (
              <tr>
                <td className="empty-state" colSpan={7}>
                  {t.invoicesLoadError}
                </td>
              </tr>
            )}
            {!loading && !error && (data?.invoices.length ?? 0) === 0 && (
              <tr>
                <td className="empty-state" colSpan={7}>
                  {t.noInvoicesToday}
                </td>
              </tr>
            )}
            {!error &&
              data?.invoices.map((row) => (
                <tr key={row.invoice_id}>
                  <td className="col-invnum">{row.invoice_number}</td>
                  <td className="col-date">{row.date}</td>
                  <td className="col-type">{row.type === "walk-in" ? t.typeWalkIn : t.typeB2B}</td>
                  <td className="col-customer">
                    {row.type === "walk-in" ? "—" : row.customer_name}
                  </td>
                  <td className="col-invtotal">{fmt(row.total)}</td>
                  <td className="col-status">
                    <span className={`status-badge status-badge--${statusTone(row.status)}`}>
                      {formatStatusLabel(row.status)}
                    </span>
                  </td>
                  <td className="col-print">
                    <button
                      type="button"
                      className="invoice-print-btn"
                      onClick={() => handlePrint(row.invoice_id)}
                      disabled={printingId === row.invoice_id}
                      aria-label={t.print}
                      title={t.print}
                    >
                      {printingId === row.invoice_id ? (
                        <Loader2 size={15} className="invoice-print-btn__spinner" />
                      ) : (
                        <Printer size={15} />
                      )}
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
