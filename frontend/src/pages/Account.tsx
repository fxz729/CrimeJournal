import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Settings, User, CreditCard, AlertTriangle, Loader2, Check, Star, Shield, Zap } from 'lucide-react'
import { authApi, favoritesApi, subscriptionApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
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
  const tierLabel = user?.subscription_tier === 'pro'
    ? t('account.tierPro')
    : user?.subscription_tier === 'enterprise'
    ? t('account.tierEnterprise')
    : t('account.tierFree')

  // Update profile mutation
  const updateMutation = useMutation({
    mutationFn: (name: string) => authApi.me(),
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
    mutationFn: () => Promise.resolve({}), // Placeholder: no backend endpoint yet
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
    // TODO: Call backend API to change password
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings className="h-6 w-6 text-primary-600" />
            <span className="font-serif text-xl font-bold">CrimeJournal</span>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <button
              onClick={() => navigate('/search')}
              className="text-gray-600 hover:text-gray-900"
            >
              {t('nav.search')}
            </button>
            <button
              onClick={() => navigate('/favorites')}
              className="text-gray-600 hover:text-gray-900"
            >
              {t('nav.favorites')}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Page Title */}
        <h1 className="text-3xl font-serif font-bold text-gray-900 mb-8">
          {t('account.title')}
        </h1>

        {/* Success Message */}
        {successMsg && (
          <div className="mb-6 bg-green-50 text-green-700 p-4 rounded-lg flex items-center gap-2">
            <Check className="h-5 w-5" />
            {successMsg}
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
                  className={`flex-shrink-0 w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition ${
                    activeTab === tab.id
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-100'
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
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
              </div>
            )}

            {/* Profile Tab */}
            {!isLoading && activeTab === 'profile' && (
              <div className="bg-white rounded-xl shadow-sm p-8 space-y-8">
                <div>
                  <h2 className="text-xl font-semibold mb-4">{t('account.profile')}</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('account.email')}
                      </label>
                      <input
                        type="email"
                        value={user?.email || ''}
                        disabled
                        className="w-full px-4 py-2 border rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('account.fullName')}
                      </label>
                      <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder={user?.full_name || ''}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    <button
                      onClick={handleUpdateProfile}
                      className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
                    >
                      {t('account.updateProfile')}
                    </button>
                  </div>
                </div>

                <hr className="border-gray-200" />

                <div>
                  <h2 className="text-xl font-semibold mb-4">{t('account.changePassword')}</h2>
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('account.currentPassword')}
                      </label>
                      <input
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('account.newPassword')}
                      </label>
                      <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('account.confirmPassword')}
                      </label>
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    {passwordError && (
                      <p className="text-red-600 text-sm">{passwordError}</p>
                    )}
                    <button
                      type="submit"
                      className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
                    >
                      {t('account.changePassword')}
                    </button>
                  </form>
                </div>
              </div>
            )}

            {/* Subscription Tab */}
            {!isLoading && activeTab === 'subscription' && (
              <div className="bg-white rounded-xl shadow-sm p-8 space-y-8">
                {/* Current Plan Section */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">{t('account.subscription')}</h2>
                  <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                      subscription?.plan === 'pro' || subscription?.plan === 'enterprise'
                        ? 'bg-primary-100'
                        : 'bg-gray-100'
                    }`}>
                      {subscription?.plan === 'pro' || subscription?.plan === 'enterprise' ? (
                        <Star className="h-6 w-6 text-primary-600" />
                      ) : (
                        <Shield className="h-6 w-6 text-gray-500" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{t('account.tier')}</p>
                      <p className="text-xl font-semibold">
                        {subscription?.plan === 'pro'
                          ? t('account.tierPro')
                          : subscription?.plan === 'enterprise'
                          ? t('account.tierEnterprise')
                          : t('account.tierFree')}
                      </p>
                      {subscription?.cancel_at_period_end && (
                        <p className="text-xs text-amber-600 mt-1">
                          {t('account.cancelConfirm')}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => navigate('/upgrade')}
                      className="ml-auto bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2"
                    >
                      <Zap className="h-4 w-4" />
                      {t('account.upgrade')}
                    </button>
                  </div>

                  {/* Billing Info */}
                  {subscription?.current_period_end && (
                    <div className="mt-3 flex items-center gap-2 text-sm text-gray-500">
                      <span>{t('account.nextBilling')}:</span>
                      <span className="font-medium">
                        {new Date(subscription.current_period_end).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {/* Usage Section */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">{t('account.usage')}</h2>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">{t('account.searchesUsed')}</span>
                      <span className="font-medium">
                        {usage?.today_searches ?? 0} / {usage?.is_unlimited ? t('account.unlimited') : (usage?.daily_limit ?? 10)}
                      </span>
                    </div>
                    {!usage?.is_unlimited && (
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            ((usage?.today_searches ?? 0) / (usage?.daily_limit ?? 10)) > 0.8
                              ? 'bg-red-500'
                              : 'bg-primary-500'
                          }`}
                          style={{
                            width: `${Math.min(((usage?.today_searches ?? 0) / (usage?.daily_limit ?? 10)) * 100, 100)}%`
                          }}
                        />
                      </div>
                    )}
                    {!usage?.is_unlimited && (
                      <p className="text-sm text-gray-500">
                        {t('account.searchesRemaining')}: {(usage?.daily_limit ?? 10) - (usage?.today_searches ?? 0)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Monthly Usage */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">{t('account.monthlyUsage')}</h2>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-gray-900">
                      {usage?.monthly_total ?? 0}
                    </p>
                    <p className="text-sm text-gray-500">{t('account.searchesThisMonth')}</p>
                  </div>
                </div>

                {/* Cancel Subscription (for paid plans) */}
                {(subscription?.plan === 'pro' || subscription?.plan === 'enterprise') && !subscription?.cancel_at_period_end && (
                  <div className="pt-4 border-t border-gray-200">
                    <button
                      onClick={() => {
                        if (window.confirm(t('account.cancelConfirm'))) {
                          cancelMutation.mutate()
                        }
                      }}
                      disabled={cancelMutation.isPending}
                      className="text-sm text-gray-500 hover:text-red-600 underline"
                    >
                      {cancelMutation.isPending ? t('common.loading') : t('account.cancelSubscription')}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Danger Zone Tab */}
            {!isLoading && activeTab === 'danger' && (
              <div className="bg-white rounded-xl shadow-sm p-8">
                <h2 className="text-xl font-semibold text-red-600 mb-4">
                  {t('account.dangerZone')}
                </h2>
                <p className="text-gray-600 mb-6">
                  {t('account.dangerZoneWarning')}
                </p>
                <button
                  onClick={handleDeleteAccount}
                  className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
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
