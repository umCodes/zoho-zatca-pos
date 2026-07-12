import { FaMoneyBillWave, FaCreditCard } from "react-icons/fa";
import { useLocale } from "../context/LangContext";
import "../styles/Paymentmethodmodal.css";

type PaymentMethod = "Cash" | "Credit Card";

interface PaymentMethodModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (method: PaymentMethod) => void;
}

export function PaymentMethodModal({ isOpen, onClose, onSelect }: PaymentMethodModalProps) {
  const { t } = useLocale();

  if (!isOpen) return null;

  const handleSelect = (method: PaymentMethod) => {
    onSelect(method);
    onClose();
  };

  return (
    <div
      className="payment-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label={t.ariaPaymentMethod}
      onClick={onClose}
    >
      <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
        <h2 className="payment-modal__title">{t.selectPaymentMethod}</h2>
        <p className="payment-modal__subtitle">{t.paymentModalSubtitle}</p>

        <div className="payment-modal__grid">
          <button
            type="button"
            onClick={() => handleSelect("Cash")}
            className="payment-card payment-card--cash"
          >
            <FaMoneyBillWave className="payment-card__icon" />
            <span className="payment-card__label">{t.cash}</span>
          </button>

          <button
            type="button"
            onClick={() => handleSelect("Credit Card")}
            className="payment-card payment-card--card"
          >
            <FaCreditCard className="payment-card__icon" />
            <span className="payment-card__label">{t.card}</span>
          </button>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="payment-modal__cancel"
        >
          {t.cancel}
        </button>
      </div>
    </div>
  );
}