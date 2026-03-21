import { Link } from 'react-router-dom'
import { BookOpen, Search, Star, Zap, FileText, Shield, HelpCircle, Mail, ArrowRight, Check } from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { useI18n } from '../lib/i18n'

export default function Docs() {
  const { t } = useI18n()

  const quickStartSteps = [
    {
      icon: <FileText className="h-5 w-5" />,
      title: t('docs.howToRegister'),
      description: t('docs.howToRegisterDesc'),
    },
    {
      icon: <Search className="h-5 w-5" />,
      title: t('docs.howToSearch'),
      description: t('docs.howToSearchDesc'),
    },
    {
      icon: <Zap className="h-5 w-5" />,
      title: t('docs.howToSummarize'),
      description: t('docs.howToSummarizeDesc'),
    },
    {
      icon: <Star className="h-5 w-5" />,
      title: t('docs.howToFavorite'),
      description: t('docs.howToFavoriteDesc'),
    },
  ]

  const faqItems = [
    {
      title: t('docs.faqWhatTitle'),
      description: t('docs.faqWhatDesc'),
    },
    {
      title: t('docs.faqDataTitle'),
      description: t('docs.faqDataDesc'),
    },
    {
      title: t('docs.faqAccuracyTitle'),
      description: t('docs.faqAccuracyDesc'),
    },
    {
      title: t('docs.faqCancelSubTitle'),
      description: t('docs.faqCancelSubDesc'),
    },
    {
      title: t('docs.faqSecurityTitle'),
      description: t('docs.faqSecurityDesc'),
    },
  ]

  const planFeatures = [
    { feature: t('upgrade.f10searches'), free: true, pro: true },
    { feature: t('upgrade.basicInfo'), free: true, pro: true },
    { feature: t('upgrade.searchHistory'), free: true, pro: true },
    { feature: t('upgrade.aiSummaries'), free: false, pro: true },
    { feature: t('upgrade.entityExtraction'), free: false, pro: true },
    { feature: t('upgrade.similarCases'), free: false, pro: true },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <BookOpen className="h-8 w-8 text-primary-600" />
              <Link to="/" className="font-serif text-xl font-bold">CrimeJournal</Link>
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
            {t('docs.title')}
          </h1>
          <p className="text-xl text-gray-600">
            {t('docs.subtitle')}
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-12 space-y-16">
        {/* Quick Start */}
        <section>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-primary-600" />
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900">{t('docs.quickStart')}</h2>
          </div>
          <p className="text-gray-600 mb-8">{t('docs.quickStartDesc')}</p>
          <div className="grid md:grid-cols-2 gap-6">
            {quickStartSteps.map((step, index) => (
              <div key={index} className="bg-white p-6 rounded-xl border hover:shadow-md transition">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    {step.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">{step.title}</h3>
                    <p className="text-sm text-gray-600">{step.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Subscription Plans */}
        <section>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center">
              <Zap className="h-5 w-5 text-accent-500" />
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900">{t('docs.subscription')}</h2>
          </div>
          <p className="text-gray-600 mb-8">{t('docs.subscriptionDesc')}</p>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Free Plan */}
            <div className="bg-white p-6 rounded-xl border">
              <h3 className="text-xl font-semibold mb-2">{t('upgrade.freePlan')}</h3>
              <p className="text-3xl font-bold mb-4">$0<span className="text-base font-normal text-gray-500">{t('upgrade.perMonth')}</span></p>
              <p className="text-gray-600 mb-6">{t('upgrade.freeDesc')}</p>
              <ul className="space-y-3">
                {planFeatures.map((item, index) => (
                  <li key={index} className="flex items-center gap-2 text-sm">
                    {item.free ? (
                      <Check className="h-4 w-4 text-green-500" />
                    ) : (
                      <span className="h-4 w-4 text-gray-300">-</span>
                    )}
                    <span className={item.free ? 'text-gray-700' : 'text-gray-400'}>{item.feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Pro Plan */}
            <div className="bg-primary-50 p-6 rounded-xl border-2 border-primary-200">
              <h3 className="text-xl font-semibold mb-2 text-primary-900">{t('upgrade.proPlan')}</h3>
              <p className="text-3xl font-bold mb-4">$50<span className="text-base font-normal text-gray-500">{t('upgrade.perMonth')}</span></p>
              <p className="text-gray-600 mb-6">{t('upgrade.proDesc')}</p>
              <ul className="space-y-3">
                {planFeatures.map((item, index) => (
                  <li key={index} className="flex items-center gap-2 text-sm">
                    <Check className="h-4 w-4 text-green-500" />
                    <span className="text-gray-700">{item.feature}</span>
                  </li>
                ))}
              </ul>
              <Link
                to="/upgrade"
                className="mt-6 block w-full text-center bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700"
              >
                {t('docs.pricingPlans')} <ArrowRight className="h-4 w-4 inline" />
              </Link>
            </div>
          </div>

          {/* How to upgrade/cancel */}
          <div className="grid md:grid-cols-2 gap-6 mt-6">
            <div className="bg-white p-6 rounded-xl border">
              <h4 className="font-semibold text-gray-900 mb-2">{t('docs.howToUpgrade')}</h4>
              <p className="text-sm text-gray-600">{t('docs.howToUpgradeDesc')}</p>
            </div>
            <div className="bg-white p-6 rounded-xl border">
              <h4 className="font-semibold text-gray-900 mb-2">{t('docs.howToCancel')}</h4>
              <p className="text-sm text-gray-600">{t('docs.howToCancelDesc')}</p>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-secondary-100 rounded-lg flex items-center justify-center">
              <HelpCircle className="h-5 w-5 text-secondary-500" />
            </div>
            <h2 className="text-2xl font-serif font-bold text-gray-900">{t('docs.faq')}</h2>
          </div>
          <div className="space-y-4">
            {faqItems.map((item, index) => (
              <div key={index} className="bg-white p-6 rounded-xl border">
                <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Contact */}
        <section className="bg-white p-8 rounded-xl border text-center">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Mail className="h-6 w-6 text-primary-600" />
          </div>
          <h2 className="text-2xl font-serif font-bold text-gray-900 mb-4">{t('docs.contact')}</h2>
          <p className="text-gray-600 mb-4">{t('about.contactDesc')}</p>
          <a
            href={`mailto:${t('docs.contactEmail')}`}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            {t('docs.contactEmail')}
          </a>
        </section>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 mt-16">
        <div className="max-w-5xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-white" />
              <span className="font-serif text-lg text-white">CrimeJournal</span>
            </div>
            <div className="flex flex-wrap gap-6 text-sm">
              <Link to="/" className="hover:text-white">{t('footer.product')}</Link>
              <Link to="/about" className="hover:text-white">{t('footer.about')}</Link>
              <Link to="/docs" className="hover:text-white">{t('footer.documentation')}</Link>
              <Link to="/upgrade" className="hover:text-white">{t('footer.pricing')}</Link>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>&copy; {new Date().getFullYear()} CrimeJournal. {t('footer.rights')}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
