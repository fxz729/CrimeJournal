import { Link } from 'react-router-dom'
import { Scale, Search, BookOpen, TrendingUp } from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { useI18n } from '../lib/i18n'

export default function Home() {
  const { t } = useI18n()

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Scale className="h-8 w-8 text-primary-600" />
              <span className="font-serif text-xl font-bold">CrimeJournal</span>
            </div>
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              <Link
                to="/login"
                className="text-gray-600 hover:text-gray-900 px-3 py-2"
              >
                {t('nav.login')}
              </Link>
              <Link
                to="/register"
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
              >
                {t('nav.register')}
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-gradient-to-b from-primary-50 to-white py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-serif font-bold text-gray-900 mb-6">
            {t('home.title')}
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            {t('home.subtitle')}
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/register"
              className="bg-primary-600 text-white px-8 py-3 rounded-lg text-lg hover:bg-primary-700 inline-flex items-center gap-2"
            >
              <Search className="h-5 w-5" />
              {t('home.cta.start')}
            </Link>
            <Link
              to="/search"
              className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg text-lg hover:bg-gray-50"
            >
              {t('home.cta.demo')}
            </Link>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-serif font-bold mb-4">
              {t('home.pricing.title')}
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              {t('home.pricing.subtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl bg-gray-50">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <BookOpen className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{t('home.feature.ai')}</h3>
              <p className="text-gray-600">
                {t('home.feature.ai.desc')}
              </p>
            </div>

            <div className="p-6 rounded-xl bg-gray-50">
              <div className="w-12 h-12 bg-accent-100 rounded-lg flex items-center justify-center mb-4">
                <Search className="h-6 w-6 text-accent-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{t('home.feature.search')}</h3>
              <p className="text-gray-600">
                {t('home.feature.search.desc')}
              </p>
            </div>

            <div className="p-6 rounded-xl bg-gray-50">
              <div className="w-12 h-12 bg-secondary-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-secondary-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{t('home.feature.similar')}</h3>
              <p className="text-gray-600">
                {t('home.feature.similar.desc')}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Preview */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-serif font-bold mb-4">{t('home.pricing.title')}</h2>
          <p className="text-gray-600 mb-8">{t('home.pricing.subtitle')}</p>

          <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
            <div className="bg-white p-6 rounded-xl border">
              <h3 className="text-xl font-semibold mb-2">{t('home.pricing.free')}</h3>
              <p className="text-3xl font-bold mb-4">$0<span className="text-base font-normal text-gray-500">/month</span></p>
              <ul className="text-left space-y-2 text-gray-600 mb-6">
                <li>10 searches per day</li>
                <li>Basic case information</li>
                <li>Search history</li>
              </ul>
              <Link
                to="/register"
                className="block w-full text-center border border-gray-300 py-2 rounded-lg hover:bg-gray-50"
              >
                {t('home.cta.start')}
              </Link>
            </div>

            <div className="bg-primary-50 p-6 rounded-xl border-2 border-primary-200">
              <h3 className="text-xl font-semibold mb-2 text-primary-900">{t('home.pricing.pro')}</h3>
              <p className="text-3xl font-bold mb-4">$50<span className="text-base font-normal text-gray-500">/month</span></p>
              <ul className="text-left space-y-2 text-gray-700 mb-6">
                <li>Unlimited searches</li>
                <li>AI case summaries</li>
                <li>Entity extraction</li>
                <li>Similar case discovery</li>
              </ul>
              <Link
                to="/register?plan=pro"
                className="block w-full text-center bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700"
              >
                {t('home.cta.start')}
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Scale className="h-6 w-6 text-white" />
            <span className="font-serif text-lg text-white">CrimeJournal</span>
          </div>
          <p>AI-Powered Legal Case Research Platform</p>
          <p className="mt-4 text-sm">&copy; 2024 CrimeJournal. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
