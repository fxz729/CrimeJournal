import { useState } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Check, Shield,
  Loader2, Star, Crown, ChevronRight, Scale
} from 'lucide-react'
import { subscriptionApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'
import { useAuth } from '../lib/auth'

interface PlanInfo {
  id: string
  name: string
  price: number
  price_monthly: number
  display_price?: number
  searches_per_day: number
  ai_summaries: boolean
  entity_extraction: boolean
  similar_cases: boolean
  api_access: boolean
  team_accounts: boolean
  description: string
}

export default function Upgrade() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()

  const [upgradeSuccess, setUpgradeSuccess] = useState(false)

  const success = searchParams.get('success')
  const canceled = searchParams.get('canceled')

  const { data: plansData, isLoading: plansLoading } = useQuery({
    queryKey: ['subscriptionPlans'],
    queryFn: () => subscriptionApi.getPlans(),
  })

  const { data: subscriptionData } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => subscriptionApi.getMySubscription(),
    enabled: !!user,
  })

  const plans: Record<string, PlanInfo> = plansData?.data || {}
  const currentPlan = subscriptionData?.data?.plan || 'free'

  const upgradeMutation = useMutation({
    mutationFn: (plan: string) => subscriptionApi.upgrade(plan),
    onSuccess: (response) => {
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url
      } else {
        setUpgradeSuccess(true)
        queryClient.invalidateQueries({ queryKey: ['subscription'] })
        queryClient.invalidateQueries({ queryKey: ['profile'] })
      }
    },
    onError: (error: any) => {
      console.error('Upgrade failed:', error)
      alert(error.response?.data?.detail || t('upgrade.upgradeFailed'))
    },
  })

  const handleUpgrade = (planId: string) => {
    upgradeMutation.mutate(planId)
  }

  const checkIconClass = 'h-5 w-5 flex-shrink-0'

  return (
    <div className="min-h-screen bg-[var(--bg-secondary)] transition-colors duration-300">
      {/* Header */}
      <header className="bg-[var(--bg-primary)] border-b border-[var(--border-default)] sticky top-0 z-50 header-blur transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center shadow-sm shadow-primary-500/20">
                <Scale className="h-4 w-4 text-white" />
              </div>
              <span className="font-serif text-lg font-bold text-[var(--text-primary)]">{t('common.brand')}</span>
            </Link>
          </div>
          <div className="flex items-center gap-1.5">
            <ThemeSwitcher />
            <LanguageSwitcher />
            <div className="h-5 w-px bg-[var(--border-default)] hidden sm:block mx-1" />
            <button
              onClick={() => navigate(-1)}
              className="hidden sm:flex items-center px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
            >
              {t('nav.back')}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Success Banner */}
        {(success === 'true' || upgradeSuccess) && (
          <div className="mb-8 p-5 rounded-xl flex items-center gap-3 border animate-fade-in-up"
            style={{ background: 'var(--status-success-bg)', color: 'var(--status-success)', borderColor: 'var(--status-success)' }}>
            <Check className="h-6 w-6 flex-shrink-0" />
            <div>
              <p className="font-semibold text-lg">{t('upgrade.success')}</p>
              <p className="text-sm opacity-80">{t('upgrade.successDesc')}</p>
            </div>
          </div>
        )}

        {/* Canceled Banner */}
        {canceled === 'true' && (
          <div className="mb-8 p-5 rounded-xl flex items-center gap-3 border animate-fade-in-up"
            style={{ background: 'var(--status-warning-bg)', color: 'var(--status-warning)', borderColor: 'var(--status-warning)' }}>
            <Shield className="h-6 w-6 flex-shrink-0" />
            <div>
              <p className="font-semibold text-lg">{t('upgrade.canceled')}</p>
              <p className="text-sm opacity-80">{t('upgrade.canceledDesc')}</p>
            </div>
          </div>
        )}

        {/* Title */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-serif font-bold text-[var(--text-primary)] mb-4">
            {t('upgrade.title')}
          </h1>
          <p className="text-lg text-[var(--text-secondary)] max-w-2xl mx-auto">
            {t('upgrade.subtitle')}
          </p>
        </div>

        {/* Loading */}
        {plansLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-[var(--brand-primary)]" />
          </div>
        )}

        {/* Plans */}
        {!plansLoading && (
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {/* Free Plan */}
            <div className="card flex flex-col">
              <div className="mb-6">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ background: 'var(--bg-tertiary)' }}>
                  <Shield className="h-6 w-6 text-[var(--text-tertiary)]" />
                </div>
                <h3 className="text-lg font-bold text-[var(--text-primary)]">
                  {plans.free?.name || t('upgrade.freePlan')}
                </h3>
                <p className="text-sm text-[var(--text-tertiary)] mt-1">
                  {plans.free?.description || t('upgrade.freeDesc')}
                </p>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-3xl font-bold text-[var(--text-primary)]">
                    ${plans.free?.price || 0}
                  </span>
                  <span className="text-sm text-[var(--text-tertiary)]">{t('upgrade.perMonth')}</span>
                </div>
              </div>

              <ul className="space-y-3 flex-1">
                {[
                  { text: t('upgrade.f10searches'), enabled: true },
                  { text: t('upgrade.basicInfo'), enabled: true },
                  { text: t('upgrade.searchHistory'), enabled: true },
                  { text: t('upgrade.aiSummaries'), enabled: false },
                  { text: t('upgrade.entityExtraction'), enabled: false },
                  { text: t('upgrade.similarCases'), enabled: false },
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-3 text-sm">
                    {item.enabled ? (
                      <Check className={checkIconClass} style={{ color: 'var(--status-success)' }} />
                    ) : (
                      <span className="w-5 h-5 flex items-center justify-center text-[var(--text-tertiary)]">—</span>
                    )}
                    <span className={item.enabled ? 'text-[var(--text-secondary)]' : 'text-[var(--text-tertiary)]'}>
                      {item.text}
                    </span>
                  </li>
                ))}
              </ul>

              <div className="mt-6 pt-5 border-t border-[var(--border-default)]">
                {currentPlan === 'free' ? (
                  <button
                    disabled
                    className="w-full py-2.5 rounded-xl text-sm font-medium cursor-not-allowed"
                    style={{ background: 'var(--bg-tertiary)', color: 'var(--text-tertiary)' }}
                  >
                    {t('upgrade.currentPlan')}
                  </button>
                ) : (
                  <button
                    onClick={() => navigate('/account')}
                    className="w-full py-2.5 rounded-xl text-sm font-medium border border-[var(--border-default)] hover:bg-[var(--bg-tertiary)] transition-colors"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    {t('upgrade.downgrade')}
                  </button>
                )}
              </div>
            </div>

            {/* Pro Plan */}
            <div className="relative card flex flex-col border-2 shadow-lg" style={{ borderColor: 'var(--brand-primary)' }}>
              {/* Popular Badge */}
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="px-3 py-1 rounded-full text-xs font-semibold text-white shadow-md"
                  style={{ background: 'var(--brand-primary)' }}>
                  {t('upgrade.mostPopular')}
                </span>
              </div>

              <div className="mb-6">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ background: 'var(--brand-primary-light)' }}>
                  <Star className="h-6 w-6 text-[var(--brand-primary)]" />
                </div>
                <h3 className="text-lg font-bold text-[var(--text-primary)]">
                  {plans.pro?.name || t('upgrade.proPlan')}
                </h3>
                <p className="text-sm text-[var(--text-tertiary)] mt-1">
                  {plans.pro?.description || t('upgrade.proDesc')}
                </p>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-3xl font-bold text-[var(--text-primary)]">
                    ${plans.pro?.display_price ?? plans.pro?.price ?? 2.9}
                  </span>
                  <span className="text-sm text-[var(--text-tertiary)]">{t('upgrade.perMonth')}</span>
                </div>
              </div>

              <ul className="space-y-3 flex-1">
                {[
                  { text: t('upgrade.unlimited'), highlight: false },
                  { text: t('upgrade.basicInfo'), highlight: false },
                  { text: t('upgrade.searchHistory'), highlight: false },
                  { text: t('upgrade.aiSummaries'), highlight: true },
                  { text: t('upgrade.entityExtraction'), highlight: true },
                  { text: t('upgrade.similarCases'), highlight: true },
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-3 text-sm">
                    <Check className={checkIconClass} style={{ color: 'var(--brand-primary)' }} />
                    <span className={item.highlight ? 'font-medium text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}>
                      {item.text}
                    </span>
                  </li>
                ))}
              </ul>

              <div className="mt-6 pt-5 border-t" style={{ borderColor: 'var(--brand-primary-light)' }}>
                {currentPlan === 'pro' ? (
                  <button
                    disabled
                    className="w-full py-2.5 rounded-xl text-sm font-medium cursor-not-allowed flex items-center justify-center gap-2"
                    style={{ background: 'var(--brand-primary-light)', color: 'var(--brand-primary)' }}
                  >
                    <Check className="h-5 w-5" />
                    {t('upgrade.currentPlan')}
                  </button>
                ) : (
                  <button
                    onClick={() => handleUpgrade('pro')}
                    disabled={upgradeMutation.isPending}
                    className="w-full py-2.5 rounded-xl text-sm font-medium text-white flex items-center justify-center gap-2 transition-all shadow-md shadow-primary-500/20 hover:-translate-y-px"
                    style={{ background: 'var(--brand-primary)' }}
                  >
                    {upgradeMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {t('upgrade.processing')}
                      </>
                    ) : (
                      <>
                        {t('upgrade.upgradePro')}
                        <ChevronRight className="h-4 w-4" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>

            {/* Enterprise Plan */}
            <div className="card flex flex-col">
              <div className="mb-6">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ background: 'rgba(168,85,247,0.1)' }}>
                  <Crown className="h-6 w-6" style={{ color: '#a855f7' }} />
                </div>
                <h3 className="text-lg font-bold text-[var(--text-primary)]">
                  {plans.enterprise?.name || t('upgrade.enterprisePlan')}
                </h3>
                <p className="text-sm text-[var(--text-tertiary)] mt-1">
                  {plans.enterprise?.description || t('upgrade.enterpriseDesc')}
                </p>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-3xl font-bold text-[var(--text-primary)]">
                    ${plans.enterprise?.display_price ?? plans.enterprise?.price ?? 5.9}
                  </span>
                  <span className="text-sm text-[var(--text-tertiary)]">{t('upgrade.perMonth')}</span>
                </div>
              </div>

              <ul className="space-y-3 flex-1">
                {[
                  { text: t('upgrade.unlimited'), highlight: false },
                  { text: t('upgrade.basicInfo'), highlight: false },
                  { text: t('upgrade.searchHistory'), highlight: false },
                  { text: t('upgrade.aiSummaries'), highlight: true },
                  { text: t('upgrade.entityExtraction'), highlight: true },
                  { text: t('upgrade.similarCases'), highlight: true },
                  { text: t('upgrade.apiAccess'), highlight: true },
                  { text: t('upgrade.teamAccounts'), highlight: true },
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-3 text-sm">
                    <Check className={checkIconClass} style={{ color: '#a855f7' }} />
                    <span className={item.highlight ? 'font-medium text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}>
                      {item.text}
                    </span>
                  </li>
                ))}
              </ul>

              <div className="mt-6 pt-5 border-t border-[var(--border-default)]">
                {currentPlan === 'enterprise' ? (
                  <button
                    disabled
                    className="w-full py-2.5 rounded-xl text-sm font-medium cursor-not-allowed flex items-center justify-center gap-2"
                    style={{ background: 'rgba(168,85,247,0.1)', color: '#a855f7' }}
                  >
                    <Check className="h-5 w-5" />
                    {t('upgrade.currentPlan')}
                  </button>
                ) : (
                  <button
                    onClick={() => handleUpgrade('enterprise')}
                    disabled={upgradeMutation.isPending}
                    className="w-full py-2.5 rounded-xl text-sm font-medium text-white flex items-center justify-center gap-2 transition-all hover:-translate-y-px"
                    style={{ background: '#7c3aed' }}
                  >
                    {upgradeMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {t('upgrade.processing')}
                      </>
                    ) : (
                      <>
                        {t('upgrade.upgradeEnterprise')}
                        <ChevronRight className="h-4 w-4" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* FAQ */}
        <div className="mt-16 max-w-3xl mx-auto">
          <h2 className="text-2xl font-serif font-bold text-[var(--text-primary)] text-center mb-8">
            {t('upgrade.faqTitle')}
          </h2>
          <div className="space-y-4">
            {[
              { q: t('upgrade.faqBilling'), a: t('upgrade.faqBillingAns') },
              { q: t('upgrade.faqCancel'), a: t('upgrade.faqCancelAns') },
              { q: t('upgrade.faqPayment'), a: t('upgrade.faqPaymentAns') },
            ].map((item, idx) => (
              <div key={idx} className="card">
                <h3 className="font-semibold text-[var(--text-primary)] mb-2">{item.q}</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Stripe Note */}
        <div className="mt-12 text-center">
          <p className="text-sm text-[var(--text-tertiary)]">
            {t('upgrade.stripeNote')}
          </p>
        </div>
      </div>
    </div>
  )
}
