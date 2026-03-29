import { useNavigate } from 'react-router-dom'
import { Scale, Home } from 'lucide-react'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'

export default function NotFound() {
  const navigate = useNavigate()
  const { t } = useI18n()

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="absolute top-4 right-4">
        <LanguageSwitcher />
      </div>
      <div className="text-center px-4">
        <div className="flex items-center justify-center gap-3 mb-6">
          <Scale className="h-10 w-10 text-primary-600" />
          <span className="font-serif text-3xl font-bold">{t('common.brand')}</span>
        </div>
        <h1 className="text-9xl font-bold text-gray-200 font-serif">404</h1>
        <h2 className="text-2xl font-semibold text-gray-900 mt-4">
          {t('common.notFound')}
        </h2>
        <p className="text-gray-600 mt-2 mb-8 max-w-md mx-auto">
          {t('common.notFoundDesc')}
        </p>
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition"
        >
          <Home className="h-5 w-5" />
          {t('common.goHome')}
        </button>
      </div>
    </div>
  )
}
