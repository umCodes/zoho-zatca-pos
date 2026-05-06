import { useLocale } from "../context/LangContext";
import "../styles/OnlineOverlay.css";

const OnlineOverlay = () => {
    const {t} = useLocale()
  return (
    <div className="overlay-backdrop">
      <div className="overlay-card">

        <div className="overlay-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="24" cy="24" r="22" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5" />
            <circle
              className="offline-ring"
              cx="24" cy="24" r="14"
              stroke="rgba(255,255,255,0.35)"
              strokeWidth="1.5"
              fill="none"
              strokeLinecap="round"
            />
            <line x1="14" y1="14" x2="34" y2="34" stroke="rgba(255,120,100,0.8)" strokeWidth="1.5" strokeLinecap="round" />
            <circle cx="24" cy="24" r="3" fill="rgba(255,255,255,0.5)" />
          </svg>
        </div>

        <p className="overlay-title">{t.youAreOffline}</p>
        <p className="overlay-subtitle">{t.recheckConnection}</p>

        <button className="refresh-btn" onClick={() => window.location.reload()}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12.5 2.5A6 6 0 1 1 7 1" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
            <polyline points="7,1 10,1 10,4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          {t.refreshPage}
        </button>

      </div>
    </div>
  );
};

export default OnlineOverlay;