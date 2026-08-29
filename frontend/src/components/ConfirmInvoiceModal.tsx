import { useEffect, useRef, useState } from "react";
import { AlertTriangle } from "lucide-react";
import "../styles/ConfirmInvoiceModal.css";
import { useLocale } from "../context/LangContext";

export interface ConfirmInvoiceModalProps {
  isOpen: boolean;
  onCancel: () => void;
  onConfirm: () => Promise<void>;
}

export default function ConfirmInvoiceModal({ isOpen, onCancel, onConfirm }: ConfirmInvoiceModalProps) {
  const { t } = useLocale();
  const modalRef = useRef<HTMLDivElement>(null);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !confirming) onCancel();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [isOpen, confirming, onCancel]);

  useEffect(() => {
    if (isOpen) modalRef.current?.focus();
    if (!isOpen) setConfirming(false);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    setConfirming(true);
    try {
      await onConfirm();
    } finally {
      setConfirming(false);
    }
  };

  return (
    <div
      className="cim-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="cim-title"
      aria-describedby="cim-desc"
      onClick={(e) => {
        if (e.target === e.currentTarget && !confirming) onCancel();
      }}
    >
      <div className="cim-modal" ref={modalRef} tabIndex={-1}>
        <div className="cim-header">
          <div className="cim-icon" aria-hidden="true">
            <AlertTriangle size={20} />
          </div>
          <h2 id="cim-title" className="cim-title">
            {t.confirmInvoiceTitle}
          </h2>
        </div>

        <p id="cim-desc" className="cim-message">
          {t.confirmInvoiceWarning}
        </p>

        <div className="cim-actions">
          <button className="cim-btn cim-btn--secondary" onClick={onCancel} disabled={confirming}>
            {t.modalCancel}
          </button>
          <button className="cim-btn cim-btn--primary" onClick={handleConfirm} disabled={confirming}>
            {confirming ? t.modalSaving : t.confirmInvoiceBtn}
          </button>
        </div>
      </div>
    </div>
  );
}
