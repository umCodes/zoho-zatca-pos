import { useState } from 'react';
import '../styles/PasswordPopup.css';
import { usePassword } from '../context/PasswordContext';

interface PasswordPopupProps {
  isOpen: boolean;
  onClose?: () => void;
}

export default function PasswordPopup({ isOpen, onClose }: PasswordPopupProps) {
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState('');
  const { setPassword } = usePassword();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
        const response = await fetch(`https://zoho-zatca-pos.onrender.com/check_password`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                value: inputValue,
            }),
        });

        const data = await response.json()

        if (!data.match) return setError("Invalid Password")

        setPassword(inputValue);
        setInputValue('');
        setError('');
        onClose?.();        
    } catch (error) {
        console.error(error)
        setError("error processing password")   
    }

    if (!inputValue.trim()) {
      setError('Password cannot be empty');
      return;
    }

  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    if (error) setError('');
  };

  if (!isOpen) return null;

  return (
    <div className="password-popup-overlay">
      <div className="password-popup-container">
        <h2>Enter Password</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="password-input-group">
            <input
              type="password"
              value={inputValue}
              onChange={handleInputChange}
              placeholder="Enter your password"
              autoFocus
              disabled={false}
            />
            {error && <p className="error-message">{error}</p>}
          </div>
          
          <button type="submit" className="submit-btn">
            Submit
          </button>
        </form>
      </div>
    </div>
  );
}