import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Check, Zap, Shield, Users, Globe, ArrowLeft,
  Loader2, Star, Crown, ChevronRight, CreditCard
} from 'lucide-react'
import { subscriptionApi, authApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { useAuth } from '../lib/auth'

interface PlanInfo {
  id: string
  name: string
  price: number
  price_monthly: number
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

  // Check if redirected from success
  const success = searchParams.get('success')
  const canceled = searchParams.get('canceled')

  // Fetch available plans
  const { data: plansData, isLoading: plansLoading } = useQuery({
    queryKey: ['subscriptionPlans'],
    queryFn: () => subscriptionApi.getPlans(),
  })

  // Fetch current subscription
  const { data: subscriptionData } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => subscriptionApi.getMySubscription(),
    enabled: !!user,
  })

  const plans: Record<string, PlanInfo> = plansData?.data || {}
  const currentPlan = subscriptionData?.data?.plan || 'free'

  // Upgrade mutation
  const upgradeMutation = useMutation({
    mutationFn: (plan: string) => subscriptionApi.upgrade(plan),
    onSuccess: (response) => {
      if (response.data.checkout_url) {
        // In real Stripe integration, redirect to Stripe
        window.location.href = response.data.checkout_url
      } else {
        // Mock mode: directly upgrade
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

  const plansList = Object.values(plans)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition"
            >
              <ArrowLeft className="h-5 w-5" />
              <span className="font-serif text-xl font-bold">CrimeJournal</span>
            </button>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Success Banner */}
        {(success === 'true' || upgradeSuccess) && (
          <div className="mb-8 bg-green-50 border border-green-200 text-green-800 p-6 rounded-xl flex items-center gap-3">
            <Check className="h-6 w-6" />
            <div>
              <p className="font-semibold text-lg">{t('upgrade.success')}</p>
              <p className="text-sm">{t('upgrade.successDesc')}</p>
            </div>
          </div>
        )}

        {/* Canceled Banner */}
        {canceled === 'true' && (
          <div className="mb-8 bg-amber-50 border border-amber-200 text-amber-800 p-6 rounded-xl flex items-center gap-3">
            <CreditCard className="h-6 w-6" />
            <div>
              <p className="font-semibold text-lg">{t('upgrade.canceled')}</p>
              <p className="text-sm">{t('upgrade.canceledDesc')}</p>
            </div>
          </div>
        )}

        {/* Page Title */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-serif font-bold text-gray-900 mb-4">
            {t('upgrade.title')}
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            {t('upgrade.subtitle')}
          </p>
        </div>

        {/* Loading State */}
        {plansLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          </div>
        )}

        {/* Plans Grid */}
        {!plansLoading && (
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Plan */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 flex flex-col">
              <div className="mb-6">
                <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-gray-500" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">
                  {plans.free?.name || t('upgrade.freePlan')}
                </h3>
                <p className="text-gray-500 text-sm mt-1">
                  {plans.free?.description || t('upgrade.freeDesc')}
                </p>
                <div className="mt-4">
                  <span className="text-3xl font-bold text-gray-900">
                    ${plans.free?.price || 0}
                  </span>
                  <span className="text-gray-500">{t('upgrade.perMonth')}</span>
                </div>
              </div>

              <ul className="space-y-3 flex-1">
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span>{t('upgrade.f10searches')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span>{t('upgrade.basicInfo')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span>{t('upgrade.searchHistory')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-400">
                  <span className="h-5 w-5 flex items-center justify-center">-</span>
                  <span>{t('upgrade.aiSummaries')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-400">
                  <span className="h-5 w-5 flex items-center justify-center">-</span>
                  <span>{t('upgrade.entityExtraction')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-400">
                  <span className="h-5 w-5 flex items-center justify-center">-</span>
                  <span>{t('upgrade.similarCases')}</span>
                </li>
              </ul>

              <div className="mt-6 pt-6 border-t border-gray-100">
                {currentPlan === 'free' ? (
                  <button
                    disabled
                    className="w-full py-3 px-4 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed"
                  >
                    {t('upgrade.currentPlan')}
                  </button>
                ) : (
                  <button
                    onClick={() => navigate('/account')}
                    className="w-full py-3 px-4 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition"
                  >
                    {t('upgrade.downgrade')}
                  </button>
                )}
              </div>
            </div>

            {/* Pro Plan */}
            <div className="relative bg-gradient-to-b from-primary-50 to-white rounded-2xl shadow-xl border-2 border-primary-500 p-8 flex flex-col transform md:scale-105">
              {/* Popular Badge */}
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-primary-500 text-white text-xs font-semibold px-3 py-1 rounded-full">
                  {t('upgrade.mostPopular')}
                </span>
              </div>

              <div className="mb-6">
                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mb-4">
                  <Star className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">
                  {plans.pro?.name || t('upgrade.proPlan')}
                </h3>
                <p className="text-gray-500 text-sm mt-1">
                  {plans.pro?.description || t('upgrade.proDesc')}
                </p>
                <div className="mt-4">
                  <span className="text-3xl font-bold text-gray-900">
                    ${plans.pro?.price || 50}
                  </span>
                  <span className="text-gray-500">{t('upgrade.perMonth')}</span>
                </div>
              </div>

              <ul className="space-y-3 flex-1">
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span className="font-medium">{t('upgrade.unlimited')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span>{t('upgrade.basicInfo')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span>{t('upgrade.searchHistory')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-primary-500 flex-shrink-0" />
                  <span>{t('upgrade.aiSummaries')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-primary-500 flex-shrink-0" />
                  <span>{t('upgrade.entityExtraction')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-primary-500 flex-shrink-0" />
                  <span>{t('upgrade.similarCases')}</span>
                </li>
              </ul>

              <div className="mt-6 pt-6 border-t border-primary-100">
                {currentPlan === 'pro' ? (
                  <button
                    disabled
                    className="w-full py-3 px-4 rounded-lg bg-primary-100 text-primary-700 cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <Check className="h-5 w-5" />
                    {t('upgrade.currentPlan')}
                  </button>
                ) : (
                  <button
                    onClick={() => handleUpgrade('pro')}
                    disabled={upgradeMutation.isPending}
                    className="w-full py-3 px-4 rounded-lg bg-primary-600 text-white hover:bg-primary-700 transition flex items-center justify-center gap-2"
                  >
                    {upgradeMutation.isPending ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        {t('upgrade.processing')}
                      </>
                    ) : (
                      <>
                        {t('upgrade.upgradePro')}
                        <ChevronRight className="h-5 w-5" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>

            {/* Enterprise Plan */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 flex flex-col">
              <div className="mb-6">
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                  <Crown className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">
                  {plans.enterprise?.name || t('upgrade.enterprisePlan')}
                </h3>
                <p className="text-gray-500 text-sm mt-1">
                  {plans.enterprise?.description || t('upgrade.enterpriseDesc')}
                </p>
                <div className="mt-4">
                  <span className="text-3xl font-bold text-gray-900">
                    ${plans.enterprise?.price || 500}
                  </span>
                  <span className="text-gray-500">{t('upgrade.perMonth')}</span>
                </div>
              </div>

              <ul className="space-y-3 flex-1">
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span className="font-medium">{t('upgrade.unlimited')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span>{t('upgrade.basicInfo')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span>{t('upgrade.searchHistory')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-purple-500 flex-shrink-0" />
                  <span>{t('upgrade.aiSummaries')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-purple-500 flex-shrink-0" />
                  <span>{t('upgrade.entityExtraction')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-purple-500 flex-shrink-0" />
                  <span>{t('upgrade.similarCases')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-purple-500 flex-shrink-0" />
                  <span>{t('upgrade.apiAccess')}</span>
                </li>
                <li className="flex items-center gap-3 text-gray-700">
                  <Check className="h-5 w-5 text-purple-500 flex-shrink-0" />
                  <span>{t('upgrade.teamAccounts')}</span>
                </li>
              </ul>

              <div className="mt-6 pt-6 border-t border-gray-100">
                {currentPlan === 'enterprise' ? (
                  <button
                    disabled
                    className="w-full py-3 px-4 rounded-lg bg-purple-100 text-purple-700 cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <Check className="h-5 w-5" />
                    {t('upgrade.currentPlan')}
                  </button>
                ) : (
                  <button
                    onClick={() => handleUpgrade('enterprise')}
                    disabled={upgradeMutation.isPending}
                    className="w-full py-3 px-4 rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition flex items-center justify-center gap-2"
                  >
                    {upgradeMutation.isPending ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        {t('upgrade.processing')}
                      </>
                    ) : (
                      <>
                        {t('upgrade.contactSales')}
                        <ChevronRight className="h-5 w-5" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* FAQ Section */}
        <div className="mt-16 max-w-3xl mx-auto">
          <h2 className="text-2xl font-serif font-bold text-gray-900 text-center mb-8">
            {t('upgrade.faqTitle')}
          </h2>
          <div className="space-y-4">
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">{t('upgrade.faqBilling')}</h3>
              <p className="text-gray-600 text-sm">{t('upgrade.faqBillingAns')}</p>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">{t('upgrade.faqCancel')}</h3>
              <p className="text-gray-600 text-sm">{t('upgrade.faqCancelAns')}</p>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">{t('upgrade.faqPayment')}</h3>
              <p className="text-gray-600 text-sm">{t('upgrade.faqPaymentAns')}</p>
            </div>
          </div>
        </div>

        {/* Stripe Note */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            {t('upgrade.stripeNote')}
          </p>
        </div>
      </div>
    </div>
  )
}
