import { useTheme } from '../lib/ThemeContext'
import { useI18n } from '../lib/i18n'
import { Sun, Moon, Monitor } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'

export default function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()
  const { t } = useI18n()
  const [open, setOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const themeLabelMap: Record<string, 'theme.light' | 'theme.dark' | 'theme.system'> = {
    light: 'theme.light',
    dark: 'theme.dark',
    system: 'theme.system',
  }
  const currentLabel = themeLabelMap[theme] || 'theme.system'

  const options: { value: 'light' | 'dark' | 'system'; labelKey: 'theme.light' | 'theme.dark' | 'theme.system'; icon: React.ReactNode }[] = [
    { value: 'light', labelKey: 'theme.light', icon: <Sun className="h-4 w-4" /> },
    { value: 'dark', labelKey: 'theme.dark', icon: <Moon className="h-4 w-4" /> },
    { value: 'system', labelKey: 'theme.system', icon: <Monitor className="h-4 w-4" /> },
  ]

  const current = options.find(o => o.value === theme) || options[2]

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
        title={t(currentLabel)}
      >
        {current.icon}
      </button>
      {open && (
        <div className="absolute right-0 mt-1 w-36 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 overflow-hidden">
          {options.map((option) => (
            <button
              key={option.value}
              onClick={() => { setTheme(option.value); setOpen(false); }}
              className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                theme === option.value
                  ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20'
                  : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              {option.icon}
              {t(option.labelKey)}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
