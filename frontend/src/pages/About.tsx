import { Link } from 'react-router-dom'
import { Scale, Mail, BookOpen } from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { useI18n } from '../lib/i18n'

export default function About() {
  const { t } = useI18n()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Scale className="h-8 w-8 text-primary-600" />
              <Link to="/" className="font-serif text-xl font-bold">{t('common.brand')}</Link>
            </div>
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              <Link to="/" className="text-gray-600 hover:text-gray-900 px-3 py-2">
                {t('nav.home')}
              </Link>
              <Link to="/docs" className="text-gray-600 hover:text-gray-900 px-3 py-2">
                {t('nav.docs')}
              </Link>
              <Link to="/about" className="text-gray-600 hover:text-gray-900 px-3 py-2">
                {t('nav.about')}
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

      {/* Hero */}
      <div className="bg-gradient-to-b from-primary-50 to-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-serif font-bold text-gray-900 mb-4">
            {t('about.title')}
          </h1>
          <p className="text-xl text-gray-600">
            {t('about.subtitle')}
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-12 space-y-16">
        {/* Why */}
        <section>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Scale className="h-5 w-5 text-primary-600" />
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900">{t('about.whyTitle')}</h2>
          </div>
          <p className="text-gray-600 text-lg leading-relaxed">
            {t('about.whyDesc')}
          </p>
        </section>

        {/* Mission */}
        <section>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-accent-500" />
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900">{t('about.mission')}</h2>
          </div>
          <p className="text-gray-600 text-lg leading-relaxed">
            {t('about.missionDesc')}
          </p>
        </section>

        {/* Tech Stack */}
        <section>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-secondary-100 rounded-lg flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-secondary-500" />
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900">{t('about.techStack')}</h2>
          </div>
          <p className="text-gray-600 text-lg leading-relaxed">
            {t('about.techStackDesc')}
          </p>
        </section>

        {/* Contact */}
        <section className="bg-white p-8 rounded-xl border text-center">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Mail className="h-6 w-6 text-primary-600" />
          </div>
          <h2 className="text-2xl font-serif font-bold text-gray-900 mb-4">{t('about.contact')}</h2>
          <p className="text-gray-600 mb-4">{t('about.contactDesc')}</p>
          <a
            href="mailto:support@crimejournal.com"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            support@crimejournal.com
          </a>
        </section>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 mt-16">
        <div className="max-w-5xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="flex items-center gap-2">
              <Scale className="h-6 w-6 text-white" />
              <span className="font-serif text-lg text-white">{t('common.brand')}</span>
            </div>
            <div className="flex flex-wrap gap-6 text-sm">
              <Link to="/" className="hover:text-white">{t('footer.product')}</Link>
              <Link to="/about" className="hover:text-white">{t('footer.about')}</Link>
              <Link to="/docs" className="hover:text-white">{t('footer.documentation')}</Link>
              <Link to="/upgrade" className="hover:text-white">{t('footer.pricing')}</Link>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>&copy; {new Date().getFullYear()} {t('common.brand')}. {t('footer.rights')}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
