import { useState } from 'react';
import { FaSpinner } from 'react-icons/fa';


interface SpinnerButtonProps {
    onClick: () => void;
    label: string;
    loadingLabel: string;
    disabled?: boolean;
    className?: string;
}

function SpinnerButton({ onClick, label, loadingLabel, disabled = false, className = '' }: SpinnerButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    if (loading) return;
    setLoading(true);
    try {
      await onClick();
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      className={className}
      onClick={handleClick}
      disabled={loading || disabled}
    >
      {loading ? (
        <>
          <FaSpinner size={14} className="spin" />
          <span>
            {loadingLabel}
          </span>
        </>
      ) : label}
    </button>
  );
}


export default SpinnerButton;