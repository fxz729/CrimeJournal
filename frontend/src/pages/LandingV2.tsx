import { Link } from 'react-router-dom'
import {
  Scale, Search, Sparkles, Shield, BookOpen,
  ChevronRight, CheckCircle2, ArrowRight, Star, Quote,
  Database, TrendingUp, Layers, MessageSquare,
  Languages, Bookmark,
  Play, Menu, X, Twitter, Github, Linkedin
} from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'
import { useI18n } from '../lib/i18n'
import { useEffect, useRef, useState } from 'react'

// ─── Animated Counter ───────────────────────────────────────────────────────
function StatCounter({ target, suffix = '', label }: { target: string; suffix?: string; label: string }) {
  const [value, setValue] = useState('0')
  const ref = useRef<HTMLDivElement>(null)
  const animated = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !animated.current) {
        animated.current = true
        const num = parseInt(target.replace(/[^0-9]/g, ''))
        const duration = 1800
        const start = Date.now()
        const tick = () => {
          const progress = Math.min((Date.now() - start) / duration, 1)
          const eased = 1 - Math.pow(1 - progress, 3)
          setValue(Math.round(num * eased).toLocaleString() + suffix)
          if (progress < 1) requestAnimationFrame(tick)
        }
        requestAnimationFrame(tick)
      }
    }, { threshold: 0.5 })
    observer.observe(el)
    return () => observer.disconnect()
  }, [target, suffix])

  return (
    <div ref={ref} className="text-center">
      <div className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-primary-600 to-violet-600 bg-clip-text text-transparent">
        {value}
      </div>
      <div className="text-sm text-[var(--text-secondary)] mt-1">{label}</div>
    </div>
  )
}

// ─── Scroll-reveal hook ─────────────────────────────────────────────────────
function useScrollReveal() {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setVisible(true)
        observer.disconnect()
      }
    }, { threshold: 0.1 })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return { ref, visible }
}

// ─── Demo Search Component ──────────────────────────────────────────────────
function DemoSearch() {
  const { t } = useI18n()
  const [query, setQuery] = useState('')
  const [active, setActive] = useState(0)
  const [results, setResults] = useState<Array<{
    title: string
    court: string
    year: string
    snippet: string
    tags: string[]
    relevance: number
  }>>([])

  const demoQueries = [
    'contract breach with quantum meruit doctrine',
    'fourth amendment digital privacy search',
    'copyright fair use transformative purpose',
  ]

  const demoResults = [
    {
      title: 'United States v. Jones',
      court: 'Supreme Court of the United States',
      year: '2012',
      snippet: 'The installation of a GPS tracking device on a vehicle, and the use of that device to monitor the vehicle\'s movements, constitutes a search within the meaning of the Fourth Amendment...',
      tags: ['Constitutional Law', 'Fourth Amendment', 'GPS Tracking'],
      relevance: 96,
    },
    {
      title: 'Campbell v. Acuff-Rose Music, Inc.',
      court: 'Supreme Court of the United States',
      year: '1994',
      snippet: 'The purpose and character of the use, including whether such use is of a commercial nature, is among the factors to be weighed in determining whether a fair use...',
      tags: ['Copyright', 'Fair Use', 'Parody'],
      relevance: 89,
    },
    {
      title: 'Peevyhouse v. Garland Coal & Mining Co.',
      court: 'Oklahoma Supreme Court',
      year: '1962',
      snippet: 'Where the cost of repairs substantially exceeds the diminution in value of the land, the cost of performance may be the measure of damages...',
      tags: ['Contract Law', 'Quantum Meruit', 'Damages'],
      relevance: 82,
    },
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setActive((prev) => (prev + 1) % demoQueries.length)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const handleSearch = (q: string) => {
    setQuery(q)
    if (q.length > 3) {
      setResults(demoResults.filter(r =>
        r.title.toLowerCase().includes(q.toLowerCase()) ||
        r.snippet.toLowerCase().includes(q.toLowerCase()) ||
        r.tags.some(tag => tag.toLowerCase().includes(q.toLowerCase()))
      ))
    } else {
      setResults([])
    }
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      {/* Search Box */}
      <div className="relative">
        <div className="flex items-center bg-[var(--bg-primary)] rounded-2xl border border-[var(--border-default)] shadow-xl shadow-primary-500/5 overflow-hidden">
          <Search className="h-5 w-5 text-[var(--text-tertiary)] ml-5 flex-shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder={t('landing.demo.placeholder') || 'Search legal cases...'}
            className="flex-1 px-4 py-5 bg-transparent text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] outline-none text-base"
          />
          <Link
            to="/search"
            className="flex items-center gap-2 px-6 py-4 bg-primary-500 text-white font-medium rounded-xl m-2 hover:bg-primary-600 transition-colors"
          >
            {t('landing.demo.search')}
          </Link>
        </div>
      </div>

      {/* Demo Query Pills */}
      <div className="flex flex-wrap gap-2 mt-4 justify-center">
        {demoQueries.map((q, i) => (
          <button
            key={i}
            onClick={() => handleSearch(q)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              active === i
                ? 'bg-primary-500 text-white shadow-sm'
                : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--border-default)]'
            }`}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="mt-6 space-y-3">
          {results.map((r, i) => (
            <div
              key={i}
              className="bg-[var(--bg-primary)] rounded-xl border border-[var(--border-default)] p-5 hover:shadow-md hover:border-primary-300/50 transition-all cursor-pointer animate-fade-in-up"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <h4 className="font-semibold text-[var(--text-primary)]">{r.title}</h4>
                  <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
                    {r.court} · {r.year}
                  </p>
                </div>
                <div className="flex items-center gap-1 px-2 py-1 bg-emerald-50 dark:bg-emerald-900/20 rounded-full flex-shrink-0">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">{r.relevance}%</span>
                </div>
              </div>
              <p className="text-sm text-[var(--text-secondary)] line-clamp-2 leading-relaxed">{r.snippet}</p>
              <div className="flex gap-1.5 mt-3 flex-wrap">
                {r.tags.map((tag, j) => (
                  <span key={j} className="px-2 py-0.5 bg-[var(--bg-tertiary)] text-[var(--text-tertiary)] text-xs rounded-md">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
          <Link
            to="/search"
            className="flex items-center justify-center gap-2 py-3 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
          >
            {t('landing.demo.viewMore')} <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      )}
    </div>
  )
}

// ─── Main Landing Page ──────────────────────────────────────────────────────
export default function LandingV2() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeSection, setActiveSection] = useState('hero')
  const { t } = useI18n()

  const howRef = useScrollReveal()
  const featuresRef = useScrollReveal()
  const compareRef = useScrollReveal()
  const testimonialsRef = useScrollReveal()
  const pricingRef = useScrollReveal()

  // Track active nav section on scroll
  useEffect(() => {
    const handleScroll = () => {
      const sections = ['hero', 'how', 'features', 'compare', 'testimonials', 'pricing']
      const scrollY = window.scrollY + 200
      for (const id of sections) {
        const el = document.getElementById(id)
        if (el && el.offsetTop <= scrollY && el.offsetTop + el.offsetHeight > scrollY) {
          setActiveSection(id)
          break
        }
      }
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { id: 'how', label: t('landing.navHowItWorks') },
    { id: 'features', label: t('landing.navFeatures') },
    { id: 'compare', label: t('landing.navCompare') },
    { id: 'testimonials', label: t('landing.navReviews') },
    { id: 'pricing', label: t('landing.navPricing') },
  ]

  const features = [
    {
      icon: Sparkles,
      color: 'from-amber-400 to-orange-500',
      bgColor: 'bg-amber-50 dark:bg-amber-900/20',
      title: t('landing.feature1Title'),
      desc: t('landing.feature1Desc'),
    },
    {
      icon: Search,
      color: 'from-blue-400 to-indigo-500',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      title: t('landing.feature2Title'),
      desc: t('landing.feature2Desc'),
    },
    {
      icon: Layers,
      color: 'from-violet-400 to-purple-500',
      bgColor: 'bg-violet-50 dark:bg-violet-900/20',
      title: t('landing.feature3Title'),
      desc: t('landing.feature3Desc'),
    },
    {
      icon: BookOpen,
      color: 'from-emerald-400 to-teal-500',
      bgColor: 'bg-emerald-50 dark:bg-emerald-900/20',
      title: t('landing.feature4Title'),
      desc: t('landing.feature4Desc'),
    },
    {
      icon: Languages,
      color: 'from-rose-400 to-pink-500',
      bgColor: 'bg-rose-50 dark:bg-rose-900/20',
      title: t('landing.feature5Title'),
      desc: t('landing.feature5Desc'),
    },
    {
      icon: Bookmark,
      color: 'from-cyan-400 to-sky-500',
      bgColor: 'bg-cyan-50 dark:bg-cyan-900/20',
      title: t('landing.feature6Title'),
      desc: t('landing.feature6Desc'),
    },
  ]

  const comparisons = [
    { feature: 'Monthly Cost', westlaw: '$300+', lexis: '$200+', crimejournal: 'From $0' },
    { feature: 'Natural Language Search', westlaw: '❌', lexis: '❌', crimejournal: '✅' },
    { feature: 'AI Summarization', westlaw: '❌', lexis: 'Limited', crimejournal: '✅' },
    { feature: 'Entity Extraction', westlaw: '❌', lexis: '❌', crimejournal: '✅' },
    { feature: 'Semantic Similarity', westlaw: '❌', lexis: '❌', crimejournal: '✅' },
    { feature: 'Multi-Language', westlaw: '❌', lexis: 'Limited', crimejournal: '✅' },
    { feature: 'Response Time', westlaw: 'Slow', lexis: 'Medium', crimejournal: '< 2 seconds' },
    { feature: 'Setup Time', westlaw: 'Days', lexis: 'Days', crimejournal: '< 5 minutes' },
  ]

  const testimonials = [
    {
      quote: 'I used to spend 2 hours on case research. With CrimeJournal, I find relevant precedent in 15 minutes. The AI summary alone saves me countless hours.',
      name: 'Sarah Chen',
      role: 'Associate, Small Law Firm',
      avatar: 'SC',
      rating: 5,
    },
    {
      quote: 'The semantic search is a game-changer. I describe the facts as I understand them, and it surfaces cases I would have never found with Boolean search.',
      name: 'Michael Torres',
      role: 'Solo Practitioner',
      avatar: 'MT',
      rating: 5,
    },
    {
      quote: 'Affordable and powerful. As a solo attorney, I couldn\'t justify the Westlaw subscription. CrimeJournal gives me 90% of the value at 5% of the cost.',
      name: 'Priya Sharma',
      role: 'Independent Legal Consultant',
      avatar: 'PS',
      rating: 5,
    },
  ]

  const steps = [
    {
      number: '01',
      title: t('landing.step1Title'),
      desc: t('landing.step1Desc'),
      icon: MessageSquare,
    },
    {
      number: '02',
      title: t('landing.step2Title'),
      desc: t('landing.step2Desc'),
      icon: Database,
    },
    {
      number: '03',
      title: t('landing.step3Title'),
      desc: t('landing.step3Desc'),
      icon: Sparkles,
    },
  ]

  return (
    <div className="min-h-screen">
      {/* ─── Navigation ─────────────────────────────────────────────────── */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[var(--bg-primary)]/80 backdrop-blur-xl border-b border-[var(--border-default)]/50 transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center shadow-lg shadow-primary-500/25">
                <Scale className="h-5 w-5 text-white" />
              </div>
              <span className="font-serif text-xl font-bold text-[var(--text-primary)]">CrimeJournal</span>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-50 dark:bg-emerald-900/30 rounded-full text-xs font-medium text-emerald-600 dark:text-emerald-400 ml-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                {t('landing.beta')}
              </span>
            </div>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <a
                  key={link.id}
                  href={`#${link.id}`}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    activeSection === link.id
                      ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20'
                      : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)]'
                  }`}
                >
                  {link.label}
                </a>
              ))}
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              <ThemeSwitcher />
              <LanguageSwitcher />
              <div className="h-5 w-px bg-[var(--border-default)] hidden sm:block" />
              <Link to="/login" className="hidden sm:flex items-center px-3.5 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors">
                {t('nav.login')}
              </Link>
              <Link to="/register" className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg text-sm font-medium hover:bg-primary-600 transition-colors shadow-sm shadow-primary-500/20 hover:-translate-y-px">
                {t('landing.ctaStart')}
              </Link>
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]"
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-[var(--bg-primary)] border-t border-[var(--border-default)] px-4 py-4 space-y-1 animate-slide-down">
            {navLinks.map((link) => (
              <a
                key={link.id}
                href={`#${link.id}`}
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                {link.label}
              </a>
            ))}
          </div>
        )}
      </nav>

      {/* ─── Hero Section ─────────────────────────────────────────────────── */}
      <section id="hero" className="relative pt-24 pb-20 sm:pt-32 sm:pb-28 overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50/50 to-violet-50/30 dark:from-primary-950/50 dark:via-gray-900 dark:to-violet-950/20" />
        <div className="absolute top-20 right-[5%] w-72 h-72 rounded-full bg-primary-200/30 dark:bg-primary-900/20 blur-3xl" />
        <div className="absolute bottom-10 left-[5%] w-56 h-56 rounded-full bg-violet-200/25 dark:bg-violet-900/15 blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-gray-200/60 dark:border-gray-700/60 shadow-sm mb-8 animate-fade-in">
              <Sparkles className="h-3.5 w-3.5 text-amber-500" />
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400">{t('landing.heroBadge')}</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold text-[var(--text-primary)] mb-6 leading-tight tracking-tight animate-fade-in-up">
              {t('landing.heroHeadline')}{' '}
              <span className="bg-gradient-to-r from-primary-600 to-violet-600 bg-clip-text text-transparent">
                {t('landing.heroHeadlineHighlight')}
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-lg sm:text-xl text-[var(--text-secondary)] mb-10 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '80ms' }}>
              {t('landing.heroSubtitle')}
            </p>

            {/* CTA Buttons */}
            <div className="flex gap-3 justify-center flex-wrap mb-16 animate-fade-in-up" style={{ animationDelay: '160ms' }}>
              <Link
                to="/register"
                className="inline-flex items-center gap-2 px-8 py-4 bg-primary-500 text-white rounded-xl text-base font-semibold hover:bg-primary-600 transition-all shadow-xl shadow-primary-500/25 hover:-translate-y-0.5"
              >
                {t('landing.ctaStart')}
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                to="/search"
                className="inline-flex items-center gap-2 px-8 py-4 bg-[var(--bg-primary)] dark:bg-gray-800 text-[var(--text-secondary)] rounded-xl text-base font-medium border border-[var(--border-default)] dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-all shadow-sm hover:-translate-y-0.5"
              >
                <Play className="h-5 w-5" />
                {t('landing.ctaDemo')}
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap gap-6 justify-center items-center text-sm text-[var(--text-tertiary)] mb-20 animate-fade-in-up" style={{ animationDelay: '240ms' }}>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" /> {t('landing.trustNoCard')}
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" /> {t('landing.trust10Searches')}
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" /> {t('landing.trustCancel')}
              </span>
            </div>

            {/* Interactive Demo */}
            <div className="animate-fade-in-up" style={{ animationDelay: '320ms' }}>
              <DemoSearch />
            </div>
          </div>
        </div>
      </section>

      {/* ─── Stats Bar ─────────────────────────────────────────────────────── */}
      <section className="bg-gradient-to-r from-primary-600 via-indigo-600 to-violet-600 py-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-white">
            {[
              { target: '1000000', suffix: '+', label: t('landing.statCasesIndexed') },
              { target: '50', suffix: '+', label: t('landing.statJurisdictions') },
              { target: '10000', suffix: '+', label: t('landing.statProfessionals') },
              { target: '95', suffix: '%', label: t('landing.statRelevance') },
            ].map((stat, i) => (
              <StatCounter key={i} {...stat} />
            ))}
          </div>
        </div>
      </section>

      {/* ─── How it Works ─────────────────────────────────────────────────── */}
      <section id="how" ref={howRef.ref} className="py-24 bg-[var(--bg-primary)] transition-colors">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`text-center mb-16 transition-all duration-700 ${howRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <span className="inline-block px-3 py-1 bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 text-xs font-semibold rounded-full mb-4">
              {t('landing.howLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[var(--text-primary)] mb-4">
              {t('landing.howTitle')}
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
              {t('landing.howSubtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, i) => (
              <div
                key={i}
                className={`relative group p-8 rounded-2xl bg-[var(--bg-secondary)] dark:bg-gray-800/50 border border-[var(--border-default)] hover:shadow-xl hover:-translate-y-1 transition-all duration-500 ${
                  howRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
                }`}
                style={{ transitionDelay: `${i * 150}ms` }}
              >
                {/* Step number */}
                <div className="absolute -top-4 left-8 w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                  {step.number}
                </div>
                <div className={`w-14 h-14 rounded-2xl ${['bg-blue-50 dark:bg-blue-900/20', 'bg-violet-50 dark:bg-violet-900/20', 'bg-emerald-50 dark:bg-emerald-900/20'][i]} flex items-center justify-center mb-6 mt-4 group-hover:scale-110 transition-transform duration-300`}>
                  <step.icon className={`h-7 w-7 ${['text-blue-600 dark:text-blue-400', 'text-violet-600 dark:text-violet-400', 'text-emerald-600 dark:text-emerald-400'][i]}`} />
                </div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{step.title}</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{step.desc}</p>
                {i < steps.length - 1 && (
                  <div className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 z-10">
                    <ChevronRight className="h-6 w-6 text-[var(--text-tertiary)]" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Features ──────────────────────────────────────────────────────── */}
      <section id="features" ref={featuresRef.ref} className="py-24 bg-[var(--bg-secondary)] transition-colors">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`text-center mb-16 transition-all duration-700 ${featuresRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <span className="inline-block px-3 py-1 bg-violet-50 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 text-xs font-semibold rounded-full mb-4">
              {t('landing.featuresLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[var(--text-primary)] mb-4">
              {t('landing.featuresTitle')}
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
              {t('landing.featuresSubtitle')}
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <div
                key={i}
                className={`group p-7 rounded-2xl bg-[var(--bg-primary)] border border-[var(--border-default)] hover:shadow-lg hover:-translate-y-1 transition-all duration-500 ${
                  featuresRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
                }`}
                style={{ transitionDelay: `${i * 100}ms` }}
              >
                <div className={`w-12 h-12 rounded-xl ${f.bgColor} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}>
                  <f.icon className={`h-6 w-6 bg-gradient-to-br ${f.color} bg-clip-text`} style={{ color: f.color.includes('amber') ? '#f59e0b' : f.color.includes('blue') ? '#3b82f6' : f.color.includes('violet') ? '#8b5cf6' : f.color.includes('emerald') ? '#10b981' : f.color.includes('rose') ? '#f43f5e' : '#06b6d4' }} />
                </div>
                <h3 className="text-base font-semibold text-[var(--text-primary)] mb-2">{f.title}</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Comparison Table ──────────────────────────────────────────────── */}
      <section id="compare" ref={compareRef.ref} className="py-24 bg-[var(--bg-primary)] transition-colors">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`text-center mb-16 transition-all duration-700 ${compareRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <span className="inline-block px-3 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-xs font-semibold rounded-full mb-4">
              {t('landing.compareLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[var(--text-primary)] mb-4">
              {t('landing.compareTitle')}
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
              {t('landing.compareSubtitle')}
            </p>
          </div>

          <div className={`overflow-x-auto transition-all duration-700 ${compareRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <table className="w-full min-w-[600px]">
              <thead>
                <tr>
                  <th className="text-left py-4 px-6 text-sm font-semibold text-[var(--text-primary)]">Feature</th>
                  <th className="py-4 px-4 text-center text-sm font-semibold text-[var(--text-tertiary)]">{t('landing.compareWestlaw')}</th>
                  <th className="py-4 px-4 text-center text-sm font-semibold text-[var(--text-tertiary)]">{t('landing.compareLexis')}</th>
                  <th className="py-4 px-4 text-center">
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-primary-500 to-violet-600 text-white text-xs font-bold rounded-full">
                      <Scale className="h-3 w-3" /> {t('landing.compareCrimeJournal')}
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((row, i) => (
                  <tr key={i} className={`border-t border-[var(--border-default)] ${i % 2 === 0 ? 'bg-[var(--bg-secondary)]/50' : ''}`}>
                    <td className="py-4 px-6 text-sm text-[var(--text-primary)] font-medium">{row.feature}</td>
                    {[row.westlaw, row.lexis, row.crimejournal].map((val, j) => (
                      <td key={j} className="py-4 px-4 text-center text-sm">
                        {val === '✅' ? (
                          <CheckCircle2 className="h-5 w-5 text-emerald-500 mx-auto" />
                        ) : val === '❌' ? (
                          <X className="h-5 w-5 text-red-400 mx-auto" />
                        ) : val === 'Limited' ? (
                          <span className="text-amber-500 text-xs font-medium">Limited</span>
                        ) : j === 2 ? (
                          <span className="text-primary-600 dark:text-primary-400 font-semibold text-xs bg-primary-50 dark:bg-primary-900/30 px-2 py-1 rounded-full">{val}</span>
                        ) : (
                          <span className="text-[var(--text-tertiary)] text-xs">{val}</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Savings callout */}
          <div className={`mt-10 text-center transition-all duration-700 delay-300 ${compareRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="inline-flex items-center gap-3 px-6 py-4 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/20 border border-emerald-200/60 dark:border-emerald-800/40 rounded-2xl">
              <TrendingUp className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
              <div className="text-left">
                <div className="text-sm font-semibold text-emerald-800 dark:text-emerald-200">
                  {t('landing.savingsTitle')}
                </div>
                <div className="text-xs text-emerald-600 dark:text-emerald-400">
                  {t('landing.savingsSubtitle')}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Testimonials ──────────────────────────────────────────────────── */}
      <section id="testimonials" ref={testimonialsRef.ref} className="py-24 bg-[var(--bg-secondary)] transition-colors">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`text-center mb-16 transition-all duration-700 ${testimonialsRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <span className="inline-block px-3 py-1 bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 text-xs font-semibold rounded-full mb-4">
              {t('landing.testimonialsLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[var(--text-primary)] mb-4">
              {t('landing.testimonialsTitle')}
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
              {t('landing.testimonialsSubtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <div
                key={i}
                className={`p-7 rounded-2xl bg-[var(--bg-primary)] border border-[var(--border-default)] hover:shadow-lg hover:-translate-y-1 transition-all duration-500 ${
                  testimonialsRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
                }`}
                style={{ transitionDelay: `${i * 150}ms` }}
              >
                {/* Stars */}
                <div className="flex gap-0.5 mb-4">
                  {Array.from({ length: t.rating }).map((_, s) => (
                    <Star key={s} className="h-4 w-4 fill-amber-400 text-amber-400" />
                  ))}
                </div>
                <Quote className="h-6 w-6 text-primary-200 dark:text-primary-800 mb-3 -ml-1" />
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-6 italic">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-violet-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                    {t.avatar}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-[var(--text-primary)]">{t.name}</div>
                    <div className="text-xs text-[var(--text-tertiary)]">{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Pricing ────────────────────────────────────────────────────────── */}
      <section id="pricing" ref={pricingRef.ref} className="py-24 bg-[var(--bg-primary)] transition-colors">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`text-center mb-16 transition-all duration-700 ${pricingRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <span className="inline-block px-3 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs font-semibold rounded-full mb-4">
              {t('landing.pricingLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[var(--text-primary)] mb-4">
              {t('landing.pricingTitle')}
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
              {t('landing.pricingSubtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {/* Free */}
            <div className={`rounded-2xl p-8 border border-[var(--border-default)] bg-[var(--bg-primary)] hover:shadow-lg transition-all ${
              pricingRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
            }`} style={{ transitionDelay: '0ms' }}>
              <div className="text-sm font-semibold text-[var(--text-secondary)] mb-1">{t('landing.planFree')}</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-[var(--text-primary)]">$0</span>
                <span className="text-sm text-[var(--text-tertiary)]">/month</span>
              </div>
              <p className="text-xs text-[var(--text-tertiary)] mb-6">{t('landing.planFreeDesc')}</p>
              <ul className="space-y-3 mb-8">
                {[
                  t('landing.planFree10Searches'),
                  t('landing.planFreeBasic'),
                  t('landing.planFreeHistory'),
                  t('landing.planFreeSupport'),
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-2.5 text-sm text-[var(--text-secondary)]">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
              <Link to="/register" className="block w-full text-center py-3 rounded-xl border-2 border-[var(--border-default)] text-[var(--text-secondary)] font-semibold hover:bg-[var(--bg-tertiary)] transition-colors">
                {t('landing.ctaStart')}
              </Link>
            </div>

            {/* Pro - Highlighted */}
            <div className={`relative rounded-2xl p-8 bg-gradient-to-br from-primary-50/80 to-violet-50/60 dark:from-primary-950/40 dark:to-violet-950/30 border-2 border-primary-300/60 dark:border-primary-700/60 shadow-xl shadow-primary-500/10 hover:shadow-2xl hover:-translate-y-1 transition-all ${
              pricingRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
            }`} style={{ transitionDelay: '150ms' }}>
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-gradient-to-r from-primary-500 to-violet-600 text-white text-xs font-bold rounded-full shadow-lg">
                {t('landing.planPopular')}
              </div>
              <div className="text-sm font-semibold text-primary-600 dark:text-primary-400 mb-1">{t('landing.planPro')}</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-[var(--text-primary)]">$2.9</span>
                <span className="text-sm text-[var(--text-tertiary)]">/month</span>
              </div>
              <p className="text-xs text-[var(--text-tertiary)] mb-6">{t('landing.planProDesc')}</p>
              <ul className="space-y-3 mb-8">
                {[
                  t('landing.planProUnlimited'),
                  t('landing.planProSummaries'),
                  t('landing.planProEntities'),
                  t('landing.planProSimilar'),
                  t('landing.planProTranslation'),
                  t('landing.planProLibrary'),
                  t('landing.planProSupport'),
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-2.5 text-sm text-[var(--text-secondary)]">
                    <CheckCircle2 className="h-4 w-4 text-primary-500 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
              <Link to="/register?plan=pro" className="block w-full text-center py-3 rounded-xl bg-gradient-to-r from-primary-500 to-violet-600 text-white font-semibold hover:opacity-90 transition-opacity shadow-md">
                Start Pro
              </Link>
            </div>

            {/* Enterprise */}
            <div className={`rounded-2xl p-8 border border-[var(--border-default)] bg-[var(--bg-primary)] hover:shadow-lg transition-all ${
              pricingRef.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
            }`} style={{ transitionDelay: '300ms' }}>
              <div className="text-sm font-semibold text-[var(--text-secondary)] mb-1">{t('landing.planEnterprise')}</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-[var(--text-primary)]">$5.9</span>
                <span className="text-sm text-[var(--text-tertiary)]">/month</span>
              </div>
              <p className="text-xs text-[var(--text-tertiary)] mb-6">{t('landing.planEnterpriseDesc')}</p>
              <ul className="space-y-3 mb-8">
                {[
                  t('landing.planEnterpriseAll'),
                  t('landing.planEnterpriseApi'),
                  t('landing.planEnterpriseTeam'),
                  t('landing.planEnterpriseCustom'),
                  t('landing.planEnterpriseSupport'),
                  t('landing.planEnterpriseSla'),
                  t('landing.planEnterpriseData'),
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-2.5 text-sm text-[var(--text-secondary)]">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
              <Link to="/register?plan=enterprise" className="block w-full text-center py-3 rounded-xl border-2 border-[var(--border-default)] text-[var(--text-secondary)] font-semibold hover:bg-[var(--bg-tertiary)] transition-colors">
                Start Enterprise
              </Link>
            </div>
          </div>

          {/* Money back guarantee */}
          <p className="text-center text-sm text-[var(--text-tertiary)] mt-8">
            <Shield className="h-4 w-4 inline mr-1" />
            {t('landing.guarantee')}
          </p>
        </div>
      </section>

      {/* ─── CTA Section ────────────────────────────────────────────────────── */}
      <section className="py-20 bg-gradient-to-br from-primary-600 via-indigo-700 to-violet-700 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-white blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-72 h-72 rounded-full bg-white blur-3xl" />
        </div>
        <div className="relative max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white mb-4">
            {t('landing.ctaReady')}
          </h2>
          <p className="text-white/80 mb-10 text-lg max-w-xl mx-auto">
            {t('landing.ctaJoin')}
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-primary-700 rounded-xl text-base font-bold hover:bg-white/90 transition-all shadow-xl hover:-translate-y-0.5"
            >
              {t('landing.ctaStart')}
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              to="/search"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 backdrop-blur-sm text-white rounded-xl text-base font-medium border border-white/20 hover:bg-white/20 transition-all"
            >
              <Play className="h-5 w-5" />
              {t('landing.ctaDemo')}
            </Link>
          </div>
        </div>
      </section>

      {/* ─── Footer ────────────────────────────────────────────────────────── */}
      <footer className="bg-[var(--text-primary)] dark:bg-gray-950 text-gray-400 dark:text-gray-500 py-16 transition-colors">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
            {/* Brand */}
            <div className="lg:col-span-1">
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center">
                  <Scale className="h-5 w-5 text-white" />
                </div>
                <span className="font-serif text-lg text-white font-bold">CrimeJournal</span>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed mb-4">
                {t('landing.footerTagline')}
              </p>
              <div className="flex gap-3">
                <a href="#" className="w-9 h-9 rounded-lg bg-gray-800 flex items-center justify-center hover:bg-gray-700 transition-colors">
                  <Twitter className="h-4 w-4" />
                </a>
                <a href="#" className="w-9 h-9 rounded-lg bg-gray-800 flex items-center justify-center hover:bg-gray-700 transition-colors">
                  <Github className="h-4 w-4" />
                </a>
                <a href="#" className="w-9 h-9 rounded-lg bg-gray-800 flex items-center justify-center hover:bg-gray-700 transition-colors">
                  <Linkedin className="h-4 w-4" />
                </a>
              </div>
            </div>

            {/* Product */}
            <div>
              <h4 className="text-white text-sm font-semibold mb-4">{t('landing.footerProduct')}</h4>
              <ul className="space-y-2.5">
                {[t('landing.footerFeatures'), t('landing.footerPricing'), t('landing.footerApiDocs'), t('landing.footerChangelog'), t('landing.footerRoadmap')].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-sm text-gray-400 hover:text-white transition-colors">{item}</a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources */}
            <div>
              <h4 className="text-white text-sm font-semibold mb-4">{t('landing.footerResources')}</h4>
              <ul className="space-y-2.5">
                {[t('landing.footerDocs'), t('landing.footerBlog'), t('landing.footerCaseStudies'), t('landing.footerLegalTips'), t('landing.footerCommunity')].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-sm text-gray-400 hover:text-white transition-colors">{item}</a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-white text-sm font-semibold mb-4">{t('landing.footerCompany')}</h4>
              <ul className="space-y-2.5">
                {[t('landing.footerAbout'), t('landing.footerCareers'), t('landing.footerPrivacy'), t('landing.footerTerms'), t('landing.footerContact')].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-sm text-gray-400 hover:text-white transition-colors">{item}</a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-500">
              &copy; {new Date().getFullYear()} CrimeJournal. {t('footer.rights')}
            </p>
            <p className="text-xs text-gray-600">
              {t('landing.footerBuilt')}
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
