import { useCallback, useState, type ReactNode } from "react";
import { PasswordContext } from "../context/PasswordContext";


const STORAGE_KEY = 'x-password';


export function PasswordProvider({ children }: { children: ReactNode }) {
  const [password, setPasswordState] = useState<string | null>(() => {
    // Load from sessionStorage only (cleared when tab/browser closes)
    return sessionStorage.getItem(STORAGE_KEY);
  });

  const setPassword = useCallback((pwd: string) => {
    setPasswordState(pwd);
    sessionStorage.setItem(STORAGE_KEY, pwd);
  }, []);

  const clearPassword = useCallback(() => {
    setPasswordState(null);
    sessionStorage.removeItem(STORAGE_KEY);
  }, []);

  return (
    <PasswordContext.Provider value={{ password, setPassword, clearPassword, isPasswordSet: !!password }}>
      {children}
    </PasswordContext.Provider>
  );
}
