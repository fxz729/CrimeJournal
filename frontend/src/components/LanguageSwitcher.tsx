import { Globe } from 'lucide-react'
import { useI18n, Language } from '../lib/i18n'

export default function LanguageSwitcher() {
  const { language, setLanguage } = useI18n()

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'zh' : 'en')
  }

  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
      title={language === 'en' ? 'Switch to Chinese' : '切换到英文'}
    >
      <Globe className="h-4 w-4" />
      <span className="font-medium">{language === 'en' ? '中文' : 'EN'}</span>
    </button>
  )
}
