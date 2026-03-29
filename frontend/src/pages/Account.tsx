import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { User, CreditCard, AlertTriangle, Loader2, Check, Star, Shield, Zap, Scale } from 'lucide-react'
import { authApi, subscriptionApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'
import { useAuth } from '../lib/auth'

interface UserProfile {
  id: number
  email: string
  full_name?: string
  subscription_tier: string
  is_active: boolean
  created_at: string
}

type Tab = 'profile' | 'subscription' | 'danger'

export default function Account() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { user: authUser, logout } = useAuth()
  const queryClient = useQueryClient()

  const [activeTab, setActiveTab] = useState<Tab>('profile')
  const [fullName, setFullName] = useState('')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  // Fetch user profile
  const { data: profileData, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => authApi.me(),
    enabled: !!authUser,
  })

  const user: UserProfile | undefined = profileData?.data

  // Update profile mutation
  const updateMutation = useMutation({
    mutationFn: (name: string) => authApi.updateProfile(name),
    onSuccess: () => {
      setSuccessMsg(t('account.updated'))
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setTimeout(() => setSuccessMsg(''), 3000)
    },
  })

  // Fetch subscription data
  const { data: subscriptionData } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => subscriptionApi.getMySubscription(),
    enabled: !!authUser,
  })

  // Fetch usage data
  const { data: usageData } = useQuery({
    queryKey: ['subscriptionUsage'],
    queryFn: () => subscriptionApi.getUsage(),
    enabled: !!authUser,
  })

  const subscription = subscriptionData?.data
  const usage = usageData?.data

  // Cancel subscription mutation
  const cancelMutation = useMutation({
    mutationFn: () => subscriptionApi.cancel(),
    onSuccess: () => {
      setSuccessMsg(t('account.cancelSuccess'))
      queryClient.invalidateQueries({ queryKey: ['subscription'] })
      setTimeout(() => setSuccessMsg(''), 5000)
    },
    onError: (error: any) => {
      setSuccessMsg(error.response?.data?.detail || t('common.error'))
      setTimeout(() => setSuccessMsg(''), 5000)
    },
  })

  // Delete account mutation
  const deleteMutation = useMutation({
    mutationFn: () => Promise.resolve({}),
    onSuccess: () => {
      logout()
      navigate('/')
    },
  })

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault()
    if (fullName.trim()) {
      updateMutation.mutate(fullName.trim())
    }
  }

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordError('')
    if (newPassword !== confirmPassword) {
      setPasswordError(t('account.passwordMismatch'))
      return
    }
    if (newPassword.length < 6) {
      setPasswordError(t('account.passwordMinLength'))
      return
    }
    setSuccessMsg(t('account.passwordUpdated'))
    setCurrentPassword('')
    setNewPassword('')
    setConfirmPassword('')
    setTimeout(() => setSuccessMsg(''), 3000)
  }

  const handleDeleteAccount = () => {
    if (window.confirm(t('account.deleteConfirm'))) {
      deleteMutation.mutate()
    }
  }

  const tabs = [
    { id: 'profile' as Tab, label: t('account.profile'), icon: User },
    { id: 'subscription' as Tab, label: t('account.subscription'), icon: CreditCard },
    { id: 'danger' as Tab, label: t('account.dangerZone'), icon: AlertTriangle },
  ]

  return (
    <div className="min-h-screen bg-[var(--bg-secondary)] transition-colors duration-300">
      {/* Header */}
      <header className="bg-[var(--bg-primary)] border-b border-[var(--border-default)] sticky top-0 z-50 header-blur transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center shadow-sm shadow-primary-500/20">
              <Scale className="h-4 w-4 text-white" />
            </div>
            <span className="font-serif text-lg font-bold text-[var(--text-primary)]">{t('common.brand')}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ThemeSwitcher />
            <LanguageSwitcher />
            <div className="h-5 w-px bg-[var(--border-default)] hidden sm:block mx-1" />
            <Link
              to="/search"
              className="hidden sm:flex items-center px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
            >
              {t('nav.search')}
            </Link>
            <Link
              to="/favorites"
              className="hidden sm:flex items-center px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
            >
              {t('nav.favorites')}
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-10">
        {/* Page Title */}
        <h1 className="text-3xl font-serif font-bold text-[var(--text-primary)] mb-8">
          {t('account.title')}
        </h1>

        {/* Success Message */}
        {successMsg && (
          <div className="mb-6 p-4 rounded-xl flex items-center gap-3 border animate-fade-in-up"
            style={{ background: 'var(--status-success-bg)', color: 'var(--status-success)', borderColor: 'var(--status-success)' }}>
            <Check className="h-5 w-5 flex-shrink-0" />
            <p className="text-sm font-medium">{successMsg}</p>
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar Tabs */}
          <div className="w-full md:w-48 flex-shrink-0">
            <nav className="flex md:flex-col gap-1 overflow-x-auto pb-2 md:pb-0">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-shrink-0 w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left text-sm font-medium transition-all duration-150 ${
                    activeTab === tab.id
                      ? 'bg-[var(--brand-primary-light)] text-[var(--brand-primary)] dark:text-[var(--brand-primary)]'
                      : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)]'
                  }`}
                >
                  <tab.icon className="h-5 w-5 flex-shrink-0" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="flex-1">
            {isLoading && (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-[var(--brand-primary)]" />
              </div>
            )}

            {/* Profile Tab */}
            {!isLoading && activeTab === 'profile' && (
              <div className="card space-y-8">
                <div>
                  <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-5">{t('account.profile')}</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
                        {t('account.email')}
                      </label>
                      <input
                        type="email"
                        value={user?.email || ''}
                        disabled
                        className="w-full px-4 py-2.5 rounded-xl border border-[var(--border-default)] bg-[var(--bg-tertiary)] text-[var(--text-tertiary)] cursor-not-allowed text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
                        {t('account.fullName')}
                      </label>
                      <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder={user?.full_name || ''}
                        className="w-full px-4 py-2.5 rounded-xl border border-[var(--border-default)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent transition-all"
                      />
                    </div>
                    <button
                      onClick={handleUpdateProfile}
                      className="btn-primary"
                    >
                      {t('account.updateProfile')}
                    </button>
                  </div>
                </div>

                <hr className="border-[var(--border-default)]" />

                <div>
                  <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-5">{t('account.changePassword')}</h2>
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
                        {t('account.currentPassword')}
                      </label>
                      <input
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="w-full px-4 py-2.5 rounded-xl border border-[var(--border-default)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
                        {t('account.newPassword')}
                      </label>
                      <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full px-4 py-2.5 rounded-xl border border-[var(--border-default)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
                        {t('account.confirmPassword')}
                      </label>
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full px-4 py-2.5 rounded-xl border border-[var(--border-default)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent transition-all"
                      />
                    </div>
                    {passwordError && (
                      <p className="text-sm font-medium" style={{ color: 'var(--status-error)' }}>{passwordError}</p>
                    )}
                    <button
                      type="submit"
                      className="btn-primary"
                    >
                      {t('account.changePassword')}
                    </button>
                  </form>
                </div>
              </div>
            )}

            {/* Subscription Tab */}
            {!isLoading && activeTab === 'subscription' && (
              <div className="card space-y-8">
                {/* Current Plan */}
                <div>
                  <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-5">{t('account.subscription')}</h2>
                  <div className="flex items-center gap-4 p-5 rounded-xl border border-[var(--border-default)]" style={{ background: 'var(--bg-tertiary)' }}>
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      subscription?.plan === 'pro' || subscription?.plan === 'enterprise'
                        ? 'bg-[var(--brand-primary-light)]'
                        : 'bg-[var(--bg-primary)]'
                    }`}>
                      {subscription?.plan === 'pro' || subscription?.plan === 'enterprise' ? (
                        <Star className="h-6 w-6 text-[var(--brand-primary)]" />
                      ) : (
                        <Shield className="h-6 w-6 text-[var(--text-tertiary)]" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm text-[var(--text-tertiary)]">{t('account.tier')}</p>
                      <p className="text-xl font-semibold text-[var(--text-primary)]">
                        {subscription?.plan === 'pro'
                          ? t('account.tierPro')
                          : subscription?.plan === 'enterprise'
                          ? t('account.tierEnterprise')
                          : t('account.tierFree')}
                      </p>
                      {subscription?.cancel_at_period_end && (
                        <p className="text-xs mt-1" style={{ color: 'var(--status-warning)' }}>
                          {t('account.cancelConfirm')}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => navigate('/upgrade')}
                      className="ml-auto btn-primary flex items-center gap-2"
                    >
                      <Zap className="h-4 w-4" />
                      {t('account.upgrade')}
                    </button>
                  </div>

                  {subscription?.current_period_end && (
                    <div className="mt-3 flex items-center gap-2 text-sm text-[var(--text-tertiary)]">
                      <span>{t('account.nextBilling')}:</span>
                      <span className="font-medium text-[var(--text-secondary)]">
                        {new Date(subscription.current_period_end).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {/* Usage */}
                <div>
                  <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-5">{t('account.usage')}</h2>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-[var(--text-secondary)]">{t('account.searchesUsed')}</span>
                      <span className="font-medium text-[var(--text-primary)]">
                        {usage?.today_searches ?? 0} / {usage?.is_unlimited ? t('account.unlimited') : (usage?.daily_limit ?? 10)}
                      </span>
                    </div>
                    {!usage?.is_unlimited && (
                      <div className="w-full rounded-full h-2" style={{ background: 'var(--bg-tertiary)' }}>
                        <div
                          className="h-2 rounded-full transition-all duration-300"
                          style={{
                            background: ((usage?.today_searches ?? 0) / (usage?.daily_limit ?? 10)) > 0.8
                              ? 'var(--status-error)'
                              : 'var(--brand-primary)',
                            width: `${Math.min(((usage?.today_searches ?? 0) / (usage?.daily_limit ?? 10)) * 100, 100)}%`
                          }}
                        />
                      </div>
                    )}
                    {!usage?.is_unlimited && (
                      <p className="text-sm text-[var(--text-tertiary)]">
                        {t('account.searchesRemaining')}: {(usage?.daily_limit ?? 10) - (usage?.today_searches ?? 0)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Monthly Usage */}
                <div>
                  <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-5">{t('account.monthlyUsage')}</h2>
                  <div className="p-5 rounded-xl border border-[var(--border-default)]" style={{ background: 'var(--bg-tertiary)' }}>
                    <p className="text-3xl font-bold text-[var(--text-primary)]">
                      {usage?.monthly_total ?? 0}
                    </p>
                    <p className="text-sm text-[var(--text-tertiary)] mt-1">{t('account.searchesThisMonth')}</p>
                  </div>
                </div>

                {/* Cancel Subscription */}
                {(subscription?.plan === 'pro' || subscription?.plan === 'enterprise') && !subscription?.cancel_at_period_end && (
                  <div className="pt-4 border-t border-[var(--border-default)]">
                    <button
                      onClick={() => {
                        if (window.confirm(t('account.cancelConfirm'))) {
                          cancelMutation.mutate()
                        }
                      }}
                      disabled={cancelMutation.isPending}
                      className="text-sm text-[var(--text-tertiary)] hover:text-[var(--status-error)] underline transition-colors"
                    >
                      {cancelMutation.isPending ? t('common.loading') : t('account.cancelSubscription')}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Danger Zone Tab */}
            {!isLoading && activeTab === 'danger' && (
              <div className="card">
                <h2 className="text-lg font-semibold mb-2" style={{ color: 'var(--status-error)' }}>
                  {t('account.dangerZone')}
                </h2>
                <p className="text-[var(--text-secondary)] mb-6 text-sm">
                  {t('account.dangerZoneWarning')}
                </p>
                <button
                  onClick={handleDeleteAccount}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-all shadow-md"
                  style={{ background: 'var(--status-error)' }}
                >
                  {t('account.deleteAccount')}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
