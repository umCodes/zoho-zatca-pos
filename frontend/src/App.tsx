import { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import './App.css'
import type { Item } from './types';
import CartTable from './components/CartTable';
import B2BCartTable from './components/B2BCartTable';
import RecentInvoices from './components/RecentInvoices';
import { CartProvider } from './providers/CartProvider';
import { useLocale } from './context/LangContext';
import OnlineOverlay from './components/OnlineOverlay';
import PasswordPopup from './components/PasswordPopup';
import { usePassword } from './context/PasswordContext';
import { apiUrl } from './env';
import { printPdf } from './utils/printPdf';
import { getCached, setCached } from './utils/apiCache';

const ITEMS_CACHE_KEY = 'items';
const ITEMS_CACHE_TTL_MS = 5 * 60 * 1000; // item catalog changes rarely

type Tab = 'walk-in' | 'b2b' | 'recent';

export interface NoticeState {
  message: string;
  invoiceId?: string;
}

function App() {
  const [items, setItems] = useState<Item[]>([])
  const [itemsLoading, setItemsLoading] = useState(true)
  const [itemsError, setItemsError] = useState(false)
  const {locale, t, setLocale, dir} = useLocale()
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [tab, setTab] = useState<Tab>('walk-in')
  const [notice, setNotice] = useState<NoticeState | null>(null)

  const { password, isPasswordSet } = usePassword();
  const [showPasswordPopup, setShowPasswordPopup] = useState(!isPasswordSet);

  // Success notice auto-dismisses after ~2.5s (spec §9)
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(null), 2500);
    return () => clearTimeout(timer);
  }, [notice]);

  const handlePrintNotice = async () => {
    if (!notice?.invoiceId) return;
    try {
      await printPdf(`${apiUrl}/invoice/${notice.invoiceId}/pdf`, { "x-password": password || "" });
    } catch (err) {
      console.error("Failed to print invoice:", err);
    }
  };
  
  useEffect(() => {
    const goOnline = () => setIsOnline(true);
    const goOffline = () => setIsOnline(false);

    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);

    
    const checkConnectivity = async () => {
    try {
      // Fetch a tiny, reliably-available resource
      // The timestamp busts the cache so the browser doesn't serve a stale response
      await fetch("https://www.google.com/favicon.ico?_=" + Date.now(), {
        mode: "no-cors",
        cache: "no-store",
      });
      setIsOnline(true);
    } catch {
      setIsOnline(false);
    }
  };
  checkConnectivity()

    // Cleanup is important — avoid duplicate listeners
    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
    };
  }, []);

  useEffect(() => {
  if (!isPasswordSet) return;

  const cached = getCached<Item[]>(ITEMS_CACHE_KEY);
  if (cached) {
    setItems(cached);
    setItemsLoading(false);
    return;
  }

  fetch(`${apiUrl}/items`, { headers: { "x-password": password || "" } })
    .then(res => {
      if (!res.ok) throw new Error("Failed to fetch")
      return res.json()
    })
    .then(data => {
      const sorted = data.sort((a: Item, b: Item) => parseInt(a.sku) - parseInt(b.sku));
      setCached(ITEMS_CACHE_KEY, sorted, ITEMS_CACHE_TTL_MS);
      setItems(sorted)
      setItemsLoading(false)
    })
    .catch(() => {
      setItemsLoading(false)
      setItemsError(true)
    })
}, [isPasswordSet, password])


  return (
    <>
      <div className="app-outer" dir={dir}>
        <div className="app-shell">
          <div className="app-header-row">
            <h2 className="app-title">{t.appTitle}</h2>
            <div className="app-header-actions">
              <div className="lang-toggle" role="radiogroup" aria-label="Language">
                {(['en', 'ar', 'am'] as const).map((code) => (
                  <button
                    key={code}
                    type="button"
                    role="radio"
                    aria-checked={locale === code}
                    className={`lang-toggle__btn ${locale === code ? 'lang-toggle__btn--active' : ''}`}
                    onClick={() => setLocale(code)}
                  >
                    {code === 'en' ? 'English' : code === 'ar' ? 'العربية' : 'አማርኛ'}
                  </button>
                ))}
              </div>
              <button
                type="button"
                className="refresh-page-btn"
                onClick={() => window.location.reload()}
                aria-label={t.refreshPage}
                title={t.refreshPage}
              >
                <RefreshCw size={16} />
              </button>
            </div>
          </div>

          <div className="tab-bar" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'walk-in'}
              className={`tab-btn ${tab === 'walk-in' ? 'tab-btn--active' : ''}`}
              onClick={() => setTab('walk-in')}
            >
              {t.tabWalkIn}
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'b2b'}
              className={`tab-btn ${tab === 'b2b' ? 'tab-btn--active' : ''}`}
              onClick={() => setTab('b2b')}
            >
              {t.tabB2B}
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'recent'}
              className={`tab-btn ${tab === 'recent' ? 'tab-btn--active' : ''}`}
              onClick={() => setTab('recent')}
            >
              {t.tabRecentInvoices}
            </button>
          </div>

          {notice && (
            <div className="notice-banner" role="status">
              <span>{notice.message}</span>
              {notice.invoiceId && (
                <button type="button" className="notice-banner__print" onClick={handlePrintNotice}>
                  {t.print}
                </button>
              )}
            </div>
          )}

          <div className="tab-body">
            {tab === 'recent' ? (
              <RecentInvoices />
            ) : (
              // Separate CartProvider per tab (keyed) — switching tabs never mixes carts.
              <CartProvider key={tab}>
                {tab === 'walk-in' ? (
                  <CartTable
                    items={items}
                    itemsLoading={itemsLoading}
                    itemsError={itemsError}
                    onNotice={setNotice}
                  />
                ) : (
                  <B2BCartTable
                    items={items}
                    itemsLoading={itemsLoading}
                    itemsError={itemsError}
                    onNotice={setNotice}
                  />
                )}
              </CartProvider>
            )}
          </div>
        </div>
        {!isOnline && <OnlineOverlay />}
        <PasswordPopup isOpen={showPasswordPopup} onClose={() => setShowPasswordPopup(false)} />

      </div>
    </>
  )
}

export default App


