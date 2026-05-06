import { createContext, useContext } from 'react';

interface PasswordContextType {
  password: string | null;
  setPassword: (pwd: string) => void;
  clearPassword: () => void;
  isPasswordSet: boolean;
}

export const PasswordContext = createContext<PasswordContextType | undefined>(undefined);


export function usePassword() {
  const context = useContext(PasswordContext);
  if (!context) {
    throw new Error('usePassword must be used within PasswordProvider');
  }
  return context;
}