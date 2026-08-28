import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { LocaleProvider } from './providers/LangProvider.tsx'
import { PasswordProvider } from './providers/PasswordProvider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PasswordProvider>
    <LocaleProvider>
      <App />
    </LocaleProvider>
    </PasswordProvider>
  </StrictMode>,
)
