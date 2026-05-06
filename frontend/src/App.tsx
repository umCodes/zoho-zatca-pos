import { useEffect, useState } from 'react';
import './App.css'
import InputSearch from './components/InputSearch';
import type { Item } from './types';
import CartTable from './components/CartTable';
import { useLocale } from './context/LangContext';
import OnlineOverlay from './components/OnlineOverlay';
import PasswordPopup from './components/PasswordPopup';
import { usePassword } from './context/PasswordContext';


function App() {
  const [items, setItems] = useState<Item[]>([])
  const [itemsLoading, setItemsLoading] = useState(true)
  const [itemsError, setItemsError] = useState(false)
  const {locale, t, setLocale} = useLocale()
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  const { password, isPasswordSet } = usePassword();
  const [showPasswordPopup, setShowPasswordPopup] = useState(!isPasswordSet);
  
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
  fetch("https://zoho-zatca-pos.onrender.com/items", {headers: {"x-password": password || ""} })
    
    .then(res => {
      console.log(res)
      if (!res.ok) throw new Error("Failed to fetch")
      return res.json()
    })
    .then(data => {
      setItems(data.sort((a: Item, b: Item) => parseInt(a.sku) - parseInt(b.sku)))
      setItemsLoading(false)
    })
    .catch(() => {
      setItemsLoading(false)
      setItemsError(true)
    })
}, [])



  return (
    <>
      <div>
        <div>
          <header>
            <h1>
              {t.appTitle} 
            </h1>
              <InputSearch options={items} loading={itemsLoading} error={itemsError} />
            <div/>
          </header>
          <main>
            <CartTable 
              title={t.orderSummary}
            />
          </main>
          <div className='langs'>
              {locale !== "en" && <button onClick={() => setLocale("en")}>English</button>}
              {locale !== "ar" && <button onClick={() => setLocale("ar")}>العربية</button>}
              {locale !== "am" && <button onClick={() => setLocale("am")}>አማርኛ</button>}
            </div>
        </div>
        {!isOnline && <OnlineOverlay />}
        <PasswordPopup isOpen={showPasswordPopup} onClose={() => setShowPasswordPopup(false)} />

      </div>
    </>
  )
}

export default App


