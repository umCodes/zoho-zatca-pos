import { useEffect, useRef } from "react";
import "../styles/AlertModal.css";

export interface AlertModalProps {
  isOpen: boolean;
  title?: string;
  message?: string;
  okLabel?: string;
  customLabel?: string;
  onOk: () => void;
  onCustom: () => void;
  onOverlayClick?: () => void;
}

export default function AlertModal({
  isOpen,
  title = "Process complete",
  message = "Your task has been successfully completed. You can continue or take another action below.",
  okLabel = "OK",
  customLabel = "View details",
  onOk,
  onCustom,
  onOverlayClick,
}: AlertModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onOk();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [isOpen, onOk]);

  useEffect(() => {
    if (isOpen) {
      modalRef.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="am-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="am-title"
      aria-describedby="am-desc"
      onClick={(e) => {
        if (e.target === e.currentTarget) onOverlayClick?.();
      }}
    >
      <div className="am-modal" ref={modalRef} tabIndex={-1}>
        <div className="am-header">
          <div className="am-icon" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path
                d="M3.5 9.5L7 13L14.5 5.5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <h2 id="am-title" className="am-title">
            {title}
          </h2>
        </div>

        <p id="am-desc" className="am-message">
          {message}
        </p>

        <div className="am-actions">
          <button className="am-btn am-btn--secondary" onClick={onCustom}>
            {customLabel}
          </button>
          <button className="am-btn am-btn--primary" onClick={onOk}>
            {okLabel}
          </button>
        </div>
      </div>
    </div>
  );
}