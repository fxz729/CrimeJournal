import { Link } from 'react-router-dom'
import { Scale, Search, BookOpen, TrendingUp, Sparkles } from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'
import { useI18n } from '../lib/i18n'
import { useEffect, useRef, useState } from 'react'

function Counter({ target, suffix = '' }: { target: string; suffix?: string }) {
  const [value, setValue] = useState('0')
  const ref = useRef<HTMLDivElement>(null)
  const animated = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !animated.current) {
          animated.current = true
          const num = parseInt(target.replace(/[^0-9]/g, ''))
          const prefix = target.match(/^[^0-9]*/)?.[0] || ''
          const duration = 1500
          const start = Date.now()
          const tick = () => {
            const elapsed = Date.now() - start
            const progress = Math.min(elapsed / duration, 1)
            const eased = 1 - Math.pow(1 - progress, 3)
            const current = Math.round(num * eased)
            setValue(prefix + current.toLocaleString() + suffix)
            if (progress < 1) requestAnimationFrame(tick)
          }
          requestAnimationFrame(tick)
        }
      },
      { threshold: 0.5 }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [target, suffix])

  return <div ref={ref}>{value}</div>
}

export default function Home() {
  const { t } = useI18n()

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-[var(--bg-primary)]/80 border-b border-[var(--border-default)] backdrop-blur-md header-blur transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-primary-500 flex items-center justify-center shadow-md shadow-primary-500/20">
                <Scale className="h-5 w-5 text-white" />
              </div>
              <span className="font-serif text-xl font-bold text-[var(--text-primary)]">{t('common.brand')}</span>
            </div>
            <div className="flex items-center gap-2">
              <ThemeSwitcher />
              <LanguageSwitcher />
              <div className="h-5 w-px bg-[var(--border-default)] hidden sm:block" />
              <Link
                to="/login"
                className="hidden sm:flex items-center px-3.5 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                {t('nav.login')}
              </Link>
              <Link
                to="/register"
                className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg text-sm font-medium hover:bg-primary-600 transition-colors shadow-sm shadow-primary-500/20 hover:shadow-md hover:shadow-primary-500/25 hover:-translate-y-px"
              >
                {t('nav.register')}
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Dynamic gradient background - light mode */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-100 via-indigo-100 to-violet-100 dark:from-primary-950/40 dark:via-gray-900 dark:to-emerald-950/20 transition-colors duration-300" />
        {/* Floating animated orbs */}
        <div className="absolute top-16 right-[15%] w-20 h-20 rounded-full bg-gradient-to-br from-blue-400/40 to-indigo-500/30 blur-sm animate-float-slow pointer-events-none" />
        <div className="absolute top-40 left-[8%] w-14 h-14 rounded-full bg-gradient-to-br from-violet-400/35 to-purple-500/25 blur-sm animate-float-medium pointer-events-none" />
        <div className="absolute bottom-32 right-[25%] w-16 h-16 rounded-full bg-gradient-to-br from-indigo-400/30 to-blue-500/20 blur-sm animate-float-fast pointer-events-none" />
        <div className="absolute bottom-20 left-[20%] w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400/40 to-teal-500/30 blur-sm animate-float-slow-2 pointer-events-none" />
        {/* Decorative circles */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-blue-200/30 dark:bg-primary-900/10 blur-3xl -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] rounded-full bg-violet-200/20 dark:bg-emerald-900/10 blur-3xl translate-y-1/2 -translate-x-1/4" />

        <div className="relative max-w-4xl mx-auto px-4 text-center py-24 sm:py-32">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/60 dark:border-gray-700/60 shadow-sm mb-8 animate-fade-in">
            <Sparkles className="h-3.5 w-3.5 text-amber-500" />
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">{t('home.poweredByMiniMax')}</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold text-[var(--text-primary)] mb-6 leading-tight tracking-tight animate-fade-in-up" style={{ animationDelay: '50ms' }}>
            {t('home.title')}
          </h1>
          <p className="text-lg sm:text-xl text-[var(--text-secondary)] mb-10 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            {t('home.subtitle')}
          </p>
          <div className="flex gap-3 justify-center flex-wrap animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-7 py-3 bg-primary-500 text-white rounded-xl text-base font-medium hover:bg-primary-600 transition-all shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 hover:-translate-y-0.5"
            >
              <Search className="h-5 w-5" />
              {t('home.cta.start')}
            </Link>
            <Link
              to="/search"
              className="inline-flex items-center gap-2 px-7 py-3 bg-[var(--bg-primary)] dark:bg-gray-800 text-[var(--text-secondary)] dark:text-gray-300 rounded-xl text-base font-medium border border-[var(--border-default)] dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-all hover:-translate-y-0.5 shadow-sm"
            >
              {t('home.cta.demo')}
            </Link>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="py-20 bg-[var(--bg-primary)] transition-colors">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-serif font-bold text-[var(--text-primary)] mb-3">
              {t('home.features.title')}
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
              {t('home.features.subtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: BookOpen,
                iconBg: 'bg-primary-50 dark:bg-primary-900/20',
                iconColor: 'text-primary-600 dark:text-primary-400',
                title: t('home.feature.ai'),
                desc: t('home.feature.ai.desc'),
                delay: '0ms',
              },
              {
                icon: Search,
                iconBg: 'bg-emerald-50 dark:bg-emerald-900/20',
                iconColor: 'text-emerald-600 dark:text-emerald-400',
                title: t('home.feature.search'),
                desc: t('home.feature.search.desc'),
                delay: '100ms',
              },
              {
                icon: TrendingUp,
                iconBg: 'bg-violet-50 dark:bg-violet-900/20',
                iconColor: 'text-violet-600 dark:text-violet-400',
                title: t('home.feature.similar'),
                desc: t('home.feature.similar.desc'),
                delay: '200ms',
              },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="group p-8 rounded-2xl bg-[var(--bg-secondary)] dark:bg-gray-800/50 border border-[var(--border-default)] hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-default animate-fade-in-up"
                style={{ animationDelay: feature.delay }}
              >
                <div className="w-13 h-13 rounded-xl flex items-center justify-center mb-5 bg-[var(--bg-primary)] shadow-sm group-hover:scale-105 transition-transform duration-300">
                  <feature.icon className={`h-6 w-6 ${feature.iconColor}`} />
                </div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{feature.title}</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="bg-primary-500 dark:bg-primary-600 py-8">
        <div className="max-w-5xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white">
            {[
              { value: '1000000', suffix: '+', label: t('home.statCasesIndexed') },
              { value: '50', suffix: '+', label: t('home.statJurisdictions') },
              { value: 'AI', suffix: '', label: t('home.statPoweredAnalysis') },
              { value: '24/7', suffix: '', label: t('home.statAvailable') },
            ].map((stat, idx) => (
              <div key={idx}>
                <div className="text-3xl font-bold text-white/90">
                  {stat.value === 'AI' || stat.value === '24/7' ? (
                    stat.value
                  ) : (
                    <Counter target={stat.value} suffix={stat.suffix} />
                  )}
                </div>
                <div className="text-sm text-white/60 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pricing */}
      <div className="py-20 bg-[var(--bg-secondary)] transition-colors">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-serif font-bold text-[var(--text-primary)] mb-3">{t('home.pricing.title')}</h2>
          <p className="text-[var(--text-secondary)] mb-12">{t('home.pricing.subtitle')}</p>

          <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
            {/* Free */}
            <div className="bg-[var(--bg-primary)] rounded-2xl p-8 border border-[var(--border-default)] text-left shadow-sm hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-1">{t('home.pricing.free')}</h3>
              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-4xl font-bold text-[var(--text-primary)]">$0</span>
                <span className="text-sm text-[var(--text-secondary)]">{t('home.pricing.perMonth')}</span>
              </div>
              <ul className="space-y-3 mb-8">
                {[
                  t('home.pricing.free.searches'),
                  t('home.pricing.free.basic'),
                  t('home.pricing.free.history'),
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-2.5 text-sm text-[var(--text-secondary)]">
                    <span className="w-5 h-5 rounded-full bg-primary-50 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                      <svg className="w-3 h-3 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
              <Link
                to="/register"
                className="block w-full text-center py-2.5 rounded-xl border-2 border-[var(--border-default)] text-[var(--text-secondary)] font-medium hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                {t('home.cta.start')}
              </Link>
            </div>

            {/* Pro */}
            <div className="relative bg-primary-50/70 dark:bg-primary-950/30 rounded-2xl p-8 border-2 border-primary-300/60 dark:border-primary-700/60 text-left shadow-lg shadow-primary-500/5 hover:shadow-xl hover:-translate-y-0.5 transition-all">
              <div className="absolute -top-3 right-6 px-3 py-1 bg-primary-500 text-white text-xs font-bold rounded-full shadow-md">
                PRO
              </div>
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-1">{t('home.pricing.pro')}</h3>
              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-4xl font-bold text-[var(--text-primary)]">$0.9</span>
                <span className="text-sm text-[var(--text-secondary)]">{t('home.pricing.perMonth')}</span>
              </div>
              <ul className="space-y-3 mb-8">
                {[
                  t('home.pricing.pro.unlimited'),
                  t('home.pricing.pro.summaries'),
                  t('home.pricing.pro.entities'),
                  t('home.pricing.pro.similar'),
                  t('home.pricing.pro.translation'),
                  t('home.pricing.pro.formatting'),
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-2.5 text-sm text-[var(--text-secondary)]">
                    <span className="w-5 h-5 rounded-full bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center flex-shrink-0">
                      <svg className="w-3 h-3 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
              <Link
                to="/register?plan=pro"
                className="block w-full text-center py-2.5 bg-primary-500 text-white rounded-xl font-medium hover:bg-primary-600 transition-colors shadow-md shadow-primary-500/20"
              >
                {t('home.cta.start')}
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-[var(--text-primary)] dark:bg-gray-950 text-gray-400 dark:text-gray-500 py-12 transition-colors">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Scale className="h-6 w-6 text-white" />
            <span className="font-serif text-lg text-white">{t('common.brand')}</span>
          </div>
          <p className="text-gray-400">{t('footer.tagline')}</p>
          <p className="mt-4 text-sm text-gray-500">&copy; {new Date().getFullYear()} {t('common.brand')}. {t('footer.rights')}</p>
        </div>
      </footer>

      {/* Global float animations */}
      <style>{`
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          33% { transform: translateY(-18px) translateX(8px); }
          66% { transform: translateY(-8px) translateX(-6px); }
        }
        @keyframes float-medium {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          25% { transform: translateY(-14px) translateX(-10px); }
          75% { transform: translateY(-22px) translateX(5px); }
        }
        @keyframes float-fast {
          0%, 100% { transform: translateY(0px) translateX(0px) rotate(0deg); }
          50% { transform: translateY(-12px) translateX(-8px) rotate(10deg); }
        }
        @keyframes float-slow-2 {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          40% { transform: translateY(-16px) translateX(6px); }
          70% { transform: translateY(-6px) translateX(-4px); }
        }
        .animate-float-slow { animation: float-slow 7s ease-in-out infinite; }
        .animate-float-medium { animation: float-medium 5s ease-in-out infinite; }
        .animate-float-fast { animation: float-fast 4s ease-in-out infinite; }
        .animate-float-slow-2 { animation: float-slow-2 6s ease-in-out infinite; }
      `}</style>
    </div>
  )
}
