import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Scale, Mail, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react'
import { authApi } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()
  const { t } = useI18n()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await authApi.login(email, password)
      const { token: tokenData, user: userData } = res.data
      login(tokenData.access_token, userData)
      navigate('/search')
    } catch (err: any) {
      setError(err.response?.data?.detail || t('auth.loginError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-white dark:bg-gray-900 transition-colors">
      {/* Left Panel - Brand & Visual */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden flex-col justify-between p-12">
        {/* Gradient panel */}
        <div className="login-panel absolute inset-0" />
        {/* Decorative grid pattern */}
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px),
                             linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px)`,
          backgroundSize: '40px 40px'
        }} />

        {/* Decorative circles */}
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full border border-white/10" />
        <div className="absolute -top-10 -right-10 w-80 h-80 rounded-full border border-white/5" />
        <div className="absolute bottom-20 -left-20 w-60 h-60 rounded-full border border-white/10" />
        <div className="absolute bottom-10 -left-10 w-60 h-60 rounded-full border border-white/5" />

        {/* Top badge */}
        <div className="relative">
          <Link to="/" className="inline-flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-lg bg-white/10 border border-white/20 flex items-center justify-center backdrop-blur-sm group-hover:bg-white/20 transition-colors">
              <Scale className="h-5 w-5 text-amber-300" />
            </div>
            <span className="font-serif text-xl font-bold text-white tracking-wide">{t('common.brand')}</span>
          </Link>
        </div>

        {/* Center content */}
        <div className="relative">
          {/* Large decorative quote mark */}
          <div className="absolute -top-8 -left-4 text-8xl text-white/5 font-serif leading-none select-none">&ldquo;</div>

          <h2 className="text-4xl font-serif font-bold text-white leading-tight mb-6">
            {t('login.heroTitle').split('\n')[0]}<br />
            <span className="text-amber-300">{t('login.heroTitle').split('\n')[1]}</span>
          </h2>
          <p className="text-white/50 text-lg max-w-md leading-relaxed">
            {t('login.heroSubtitle')}
          </p>

          {/* Feature pills */}
          <div className="flex flex-wrap gap-3 mt-8">
            {[t('login.featureAiSummaries'), t('login.featureEntityExtraction'), t('login.featureSimilarCases')].map((tag) => (
              <span key={tag} className="px-3 py-1 rounded-full text-xs font-medium bg-white/5 border border-white/10 text-white/60">
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Bottom stats */}
        <div className="relative grid grid-cols-3 gap-6 pt-6 border-t border-white/10">
          {[
            { value: '1M+', label: t('login.statCasesIndexed') },
            { value: '50+', label: t('login.statJurisdictions') },
            { value: 'AI', label: t('login.statPoweredAnalysis') },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-2xl font-bold text-amber-300">{stat.value}</div>
              <div className="text-xs text-white/40 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top bar */}
        <div className="flex items-center justify-end gap-3 p-4">
          <ThemeSwitcher />
          <LanguageSwitcher />
        </div>

        {/* Form area */}
        <div className="flex-1 flex items-center justify-center px-6 py-8">
          <div className="w-full max-w-md">
            {/* Mobile logo */}
            <div className="lg:hidden flex items-center justify-center gap-2 mb-8">
              <Scale className="h-7 w-7 text-primary-600 dark:text-amber-400" />
              <span className="font-serif text-xl font-bold dark:text-white">{t('common.brand')}</span>
            </div>

            {/* Header */}
            <div className="mb-8">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 text-xs font-medium mb-4">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 dark:bg-amber-400" />
                {t('auth.welcome')}
              </div>
              <h1 className="text-3xl font-serif font-bold text-gray-900 dark:text-white mb-2">
                {t('auth.login')}
              </h1>
              <p className="text-gray-500 dark:text-gray-400 text-sm">
                {t('login.subtitle')}
              </p>
            </div>

            {/* Error */}
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/40">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/40 flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email field */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {t('auth.email')}
                </label>
                <div className="relative group">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 focus:border-transparent transition-all text-sm"
                    placeholder={t('auth.emailPlaceholder')}
                    required
                    style={{ paddingLeft: '2.75rem' }}
                  />
                  <Mail className="absolute start-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-primary-500 dark:group-focus-within:text-primary-400 transition-colors pointer-events-none" />
                </div>
              </div>

              {/* Password field */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {t('auth.password')}
                  </label>
                  <Link to="/forgot-password" className="text-xs text-primary-600 dark:text-primary-400 hover:underline">
                    {t('login.forgotPassword')}
                  </Link>
                </div>
                <div className="relative group">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pr-12 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-amber-500 dark:focus:ring-amber-400 focus:border-transparent transition-all text-sm"
                    placeholder={t('auth.passwordPlaceholder')}
                    required
                    style={{ paddingLeft: '2.75rem' }}
                  />
                  <Lock className="absolute start-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-amber-500 dark:group-focus-within:text-amber-400 transition-colors pointer-events-none z-10" />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                    style={{ marginTop: '-1px' }}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full relative overflow-hidden flex items-center justify-center gap-2 bg-primary-600 dark:bg-primary-500 text-white py-3.5 rounded-xl font-medium hover:bg-primary-700 dark:hover:bg-primary-400 disabled:opacity-60 disabled:cursor-not-allowed transition-all shadow-md shadow-primary-500/25 group"
              >
                <span className={loading ? 'hidden' : 'flex items-center gap-2'}>
                  {t('auth.signin')}
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </span>
                {loading && (
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                )}
              </button>
            </form>

            {/* Register link */}
            <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700 text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {t('auth.noAccount')}{' '}
                <Link to="/register" className="text-primary-600 dark:text-primary-400 font-medium hover:underline">
                  {t('auth.signup')} &rarr;
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Global styles */}
      <style>{`
        /* Left panel gradient */
        .login-panel {
          background: linear-gradient(145deg, #1e3a5f 0%, #3b82f6 50%, #1e40af 100%);
        }
        .dark .login-panel {
          background: linear-gradient(145deg, #0f1729 0%, #1a1f35 40%, #0d1829 100%);
        }
      `}</style>
    </div>
  )
}
