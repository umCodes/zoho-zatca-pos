import { useState, useRef, useEffect } from "react";
import { Building2, X, Plus } from "lucide-react";
import "../styles/CustomerSearch.css";
import type { Customer } from "../types";
import { useLocale } from "../context/LangContext";
import { usePassword } from "../context/PasswordContext";
import { apiUrl } from "../env";
import CreateCustomerModal from "./CreateCustomerModal";

interface CustomerSearchProps {
  selected: Customer | null;
  onSelect: (customer: Customer) => void;
  onClear: () => void;
}

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

function CustomerSearch({ selected, onSelect, onClear }: CustomerSearchProps) {
  const { password } = usePassword();
  const { t } = useLocale();

  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const [createModalOpen, setCreateModalOpen] = useState(false);

  const ref = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  useEffect(() => {
    if (!open) return;
    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      setError(false);
      try {
        const res = await fetch(
          `${apiUrl}/customers?search=${encodeURIComponent(query)}`,
          { headers: { "x-password": password || "" } }
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setResults(data.ok ? data.customers : []);
      } catch {
        setError(true);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, open, password]);

  const handlePick = (customer: Customer) => {
    onSelect(customer);
    setOpen(false);
    setQuery("");
  };

  return (
    <div className="customer-search-root" ref={ref}>
      <div className="customer-search-row">
        {selected ? (
          <div className="customer-selected">
            <span className="customer-avatar">{initials(selected.contact_name)}</span>
            <div className="customer-selected__info">
              <span className="customer-selected__name">{selected.contact_name}</span>
              {selected.tax_reg_no && (
                <span className="customer-selected__meta">
                  {t.newCustomerTaxRegNo}: {selected.tax_reg_no}
                </span>
              )}
            </div>
            <button type="button" className="customer-change-btn" onClick={onClear}>
              <X size={13} />
              {t.changeCustomer}
            </button>
          </div>
        ) : (
          <div className="search-field search-field--customer">
            <Building2 className="search-field__icon" size={16} />
            <input
              className="search-input"
              type="text"
              placeholder={t.customerSearchPlaceholder}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setOpen(true);
              }}
              onFocus={() => setOpen(true)}
            />
            {open && (
              <div className="dropdown-menu">
                <div className="options-list">
                  {loading && <div className="search-status loading">{t.loadingCustomers}</div>}
                  {!loading && error && (
                    <div className="search-status error">{t.customersLoadError}</div>
                  )}
                  {!loading && !error && results.length === 0 && (
                    <div className="search-status no-results">{t.noCustomerResults}</div>
                  )}
                  {!loading &&
                    !error &&
                    results.map((c) => (
                      <button
                        key={c.contact_id}
                        type="button"
                        className="customer-option"
                        onMouseDown={() => handlePick(c)}
                      >
                        <span className="customer-option__left">
                          <span className="customer-avatar customer-avatar--sm">
                            {initials(c.contact_name)}
                          </span>
                          <span className="customer-option__text">
                            <span className="customer-option__name">{c.contact_name}</span>
                            {c.tax_reg_no && (
                              <span className="customer-option__sub">{c.tax_reg_no}</span>
                            )}
                          </span>
                        </span>
                      </button>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        {!selected && (
          <button type="button" className="add-customer-btn" onClick={() => setCreateModalOpen(true)}>
            <Plus size={14} />
            {t.addCustomerBtn}
          </button>
        )}
      </div>

      <CreateCustomerModal
        isOpen={createModalOpen}
        initialQuery={query}
        onClose={() => setCreateModalOpen(false)}
        onCreated={(customer) => {
          setCreateModalOpen(false);
          handlePick(customer);
        }}
      />
    </div>
  );
}

export default CustomerSearch;
