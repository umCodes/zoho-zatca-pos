import { useState, useRef, useEffect } from "react";
import { Barcode } from "lucide-react";
import "../styles/InputSearch.css";
import type { Item } from "../types";
import { useCart } from "../context/CartContext";
import { useLocale } from "../context/LangContext";

const MAX_RESULTS = 10;

function InputSearch({ options, loading, error }: { options: Item[]; loading: boolean; error: boolean }) {
  const { addToCart } = useCart();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Item | null>(null);
  const ref = useRef<HTMLDivElement>(null);
  const { t } = useLocale();

  // Spec §5.2: focusing an empty field shows a capped result list;
  // typing narrows the same open list in place.
  const filtered = options
    .filter((o) =>
      Object.values(o).join("").toLowerCase().includes(query.toLowerCase())
    )
    .sort((a, b) => b.rate - a.rate)
    .slice(0, MAX_RESULTS);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);
  const handleBarcodeInput = (value: string) => {
    // Pattern: 99 + SKU(5 digits, starts with 1) + quantity(5 digits) + random(1 digit)
    // Total length: 2 + 5 + 5 + 1 = 13 characters
    const barcodePattern = /^99(1\d{4})(\d{5})\d$/;
    const match = value.match(barcodePattern);

    if (match) {
      const sku = match[1];                          // e.g. "10001"
      const quantity = parseInt(match[2], 10) / 1000; // e.g. "00505" → 0.505

      const item = options.find((o) => o.sku === sku);
      if (item) {
        addToCart({...item, qty: quantity });
        setQuery("");
        setOpen(false);
        return true;
      }
    }
    return false;
  };

  return (
    <div className="input-search-root">
      <div className="search-field" ref={ref}>
        <Barcode className="search-field__icon" size={17} />
        <input
          className="search-input"
          disabled={loading || error}
          type="text"
          placeholder={t.itemSearchPlaceholder}
          value={query}
          onChange={(e) => {
            const value = e.target.value;
            if (value.length === 13 && value.startsWith("99")) {
              const handled = handleBarcodeInput(value);
              if (handled) return;
            }
            setQuery(value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
        />
        {loading && (
          <div className="search-status loading">{t.loadingItems}</div>
        )}
        {error && (
          <div className="search-status error">{t.itemsLoadError}</div>
        )}
        {!loading && !error && open && filtered.length === 0 && query.length > 0 && (
          <div className="search-status no-results">{t.noResults}</div>
        )}
        {open && filtered.length > 0 && (
          <div className="dropdown-menu">
            <div className="options-list">
              {filtered.map((item) => (
                <button
                  key={item.item_id}
                  className={`option ${selected?.item_id === item.item_id ? "selected" : ""}`}
                  onMouseDown={() => {
                    setSelected(item);
                    setOpen(false);
                    setQuery("");
                    addToCart(item);
                  }}
                >
                  <span className="option__main">
                    <span className="option__left">
                      <span className="option__sku">{item.sku}</span>
                      <span className="option__name">{item.name}</span>
                      <span className="option__unit">/ {item.unit}</span>
                    </span>
                    <span className="option__price">{t.currency} {item.rate.toFixed(2)}</span>
                  </span>
                  {item.description && (
                    <span className="option__description">{item.description}</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default InputSearch;