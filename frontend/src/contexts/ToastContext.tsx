"use client";
import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

interface Toast { id: number; message: string; }
interface ToastContextType { showToast: (message: string) => void; }

const ToastContext = createContext<ToastContextType>({ showToast: () => {} });

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const showToast = useCallback((message: string) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3000);
  }, []);
  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-[100] space-y-2">
        {toasts.map((t) => (
          <div key={t.id} className="bg-white text-black text-sm px-4 py-3 rounded-lg shadow-lg animate-fade-in">
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() { return useContext(ToastContext); }
