import { useState } from "react"

export function useToast() {
  const [toasts, setToasts] = useState([])

  const toast = ({ title, description, variant = "default", duration = 5000 }) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast = { id, title, description, variant }
    
    setToasts(prev => [...prev, newToast])
    
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, duration)
    
    return { id }
  }

  const dismiss = (toastId) => {
    setToasts(prev => prev.filter(t => t.id !== toastId))
  }

  return {
    toasts,
    toast,
    dismiss
  }
}
