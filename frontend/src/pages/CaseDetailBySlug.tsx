import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft, FileText, Calendar, MapPin, Loader2, Star, Check,
  Download, Languages, ChevronDown, ChevronUp, ExternalLink, Copy, AlertCircle,
  Wifi, Clock, AlertTriangle, XCircle, Link2
} from 'lucide-react'
import { casesApi, favoritesApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'

interface CaseItem {
  id: number
  courtlistener_id: number
  case_name: string
  case_name_full?: string
  court: string
  court_id: string
  date_filed: string
  date_decided: string
  citation: string
  docket_number: string
  plain_text: string
  plain_text_formatted?: string
  html_text: string
  summary: string
  keywords: string[]
  entities: Record<string, string[]>
  source_url?: string
  slug?: string
  slug_url?: string
}

interface SimilarCase {
  id: number
  case_name: string
  court: string
  date_filed: string
  similarity: number
  slug?: string
  slug_url?: string
}

type ErrorType = 'not_found' | 'rate_limit' | 'server_error' | 'network' | 'unknown'

function getErrorInfo(status: number, message: string): { type: ErrorType; titleKey: string; descriptionKey: string; icon: typeof AlertCircle } {
  const normalizedMessage = (message || '').toLowerCase()

  if (status === 404 || message.includes('不存在') || normalizedMessage.includes('not found')) {
    return {
      type: 'not_found',
      titleKey: 'case.errorNotFound',
      descriptionKey: 'case.errorNotFoundDesc',
      icon: XCircle,
    }
  }
  if (status === 429 || message.includes('频繁') || normalizedMessage.includes('rate limit') || normalizedMessage.includes('too many request')) {
    return {
      type: 'rate_limit',
      titleKey: 'case.errorRateLimit',
      descriptionKey: 'case.errorRateLimitDesc',
      icon: Clock,
    }
  }
  if (status === 502 || status === 503 || status === 504 || message.includes('暂时不可用') || normalizedMessage.includes('service unavailable') || normalizedMessage.includes('bad gateway')) {
    return {
      type: 'server_error',
      titleKey: 'case.errorServerUnavailable',
      descriptionKey: 'case.errorServerUnavailableDesc',
      icon: Wifi,
    }
  }
  if (status === 0 || message.includes('network') || message.includes('Network') || message.includes('fetch') || message.includes('failed to fetch') || normalizedMessage.includes('network error')) {
    return {
      type: 'network',
      titleKey: 'case.errorNetwork',
      descriptionKey: 'case.errorNetworkDesc',
      icon: AlertTriangle,
    }
  }
  if (status === 401 || status === 403) {
    return {
      type: 'not_found',
      titleKey: 'case.errorAccessDenied',
      descriptionKey: 'case.errorAccessDeniedDesc',
      icon: AlertCircle,
    }
  }
  const displayMessage = message && message.length > 0 && message !== 'Request failed with status code 500'
    ? message
    : ''
  return {
    type: 'unknown',
    titleKey: 'case.errorUnexpected',
    descriptionKey: displayMessage || 'case.errorUnexpected',
    icon: AlertCircle,
  }
}

function SkeletonBlock({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700 ${className}`} />
  )
}

function CaseSkeleton() {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-100 dark:border-gray-700">
        <SkeletonBlock className="h-8 w-3/4 mb-4" />
        <div className="flex gap-4 mb-4">
          <SkeletonBlock className="h-5 w-32" />
          <SkeletonBlock className="h-5 w-40" />
          <SkeletonBlock className="h-5 w-24" />
        </div>
        <SkeletonBlock className="h-4 w-full mb-2" />
        <SkeletonBlock className="h-4 w-5/6" />
        <div className="flex gap-2 mt-4">
          <SkeletonBlock className="h-6 w-16 rounded-full" />
          <SkeletonBlock className="h-6 w-20 rounded-full" />
          <SkeletonBlock className="h-6 w-14 rounded-full" />
        </div>
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-100 dark:border-gray-700">
        <SkeletonBlock className="h-6 w-32 mb-4" />
        <SkeletonBlock className="h-4 w-full mb-2" />
        <SkeletonBlock className="h-4 w-full mb-2" />
        <SkeletonBlock className="h-4 w-4/5 mb-2" />
        <SkeletonBlock className="h-4 w-3/4" />
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-100 dark:border-gray-700">
        <SkeletonBlock className="h-6 w-32 mb-4" />
        <SkeletonBlock className="h-4 w-full mb-2" />
        <SkeletonBlock className="h-4 w-full mb-2" />
        <SkeletonBlock className="h-4 w-full mb-2" />
        <SkeletonBlock className="h-4 w-3/4 mb-2" />
        <SkeletonBlock className="h-4 w-full mb-2" />
        <SkeletonBlock className="h-4 w-5/6 mb-2" />
        <SkeletonBlock className="h-4 w-full mb-2" />
        <SkeletonBlock className="h-4 w-2/3" />
      </div>
    </div>
  )
}

function ErrorDisplay({ message, onRetry }: { message: string; onRetry: () => void }) {
  const { t } = useI18n()
  // Derive status from message for consistent error display
  const status = message.includes('404') ? 404 : message.includes('429') ? 429 : 0
  const errorInfo = getErrorInfo(status, message)
  const ErrorIcon = errorInfo.icon

  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      <div className="w-16 h-16 rounded-2xl bg-red-50 dark:bg-red-900/20 flex items-center justify-center mb-6 border border-red-100 dark:border-red-800/30">
        <ErrorIcon className="h-8 w-8 text-red-500 dark:text-red-400" />
      </div>
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{t(errorInfo.titleKey as any)}</h2>
      <p className="text-gray-500 dark:text-gray-400 text-center max-w-md mb-6">{t(errorInfo.descriptionKey as any)}</p>
      <div className="flex gap-3">
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-primary-600 dark:bg-primary-500 text-white rounded-xl hover:bg-primary-700 dark:hover:bg-primary-600 transition-colors text-sm font-medium flex items-center gap-2"
        >
          <Loader2 className="h-4 w-4" />
          {t('common.retry')}
        </button>
        <button
          onClick={() => window.history.back()}
          className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          {t('common.back')}
        </button>
      </div>
    </div>
  )
}

const TRANSLATION_LANGUAGES = [
  { value: 'English', label: 'English' },
  { value: 'Chinese', label: '中文' },
  { value: 'Spanish', label: 'Español' },
  { value: 'French', label: 'Français' },
  { value: 'German', label: 'Deutsch' },
  { value: 'Japanese', label: '日本語' },
  { value: 'Korean', label: '한국어' },
  { value: 'Arabic', label: 'العربية' },
]

/**
 * CaseDetailBySlug - Displays case details using semantic URL slugs.
 * Route: /cases/:country/:type/:slug
 * Example: /cases/us/criminal/people-v-smith-123456789/
 */
export default function CaseDetailBySlug() {
  const { country, type, slug } = useParams<{ country: string; type: string; slug: string }>()
  const navigate = useNavigate()
  const { t } = useI18n()
  const queryClient = useQueryClient()

  const [copied, setCopied] = useState(false)
  const [textExpanded, setTextExpanded] = useState(false)
  const [translateLanguage, setTranslateLanguage] = useState('Chinese')
  const [translationResult, setTranslationResult] = useState<string | null>(null)
  const [translationLoading, setTranslationLoading] = useState(false)
  const [translationCopied, setTranslationCopied] = useState(false)
  const [translationError, setTranslationError] = useState<string | null>(null)
  const [shareLinkCreated, setShareLinkCreated] = useState(false)
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const [formattedText, setFormattedText] = useState<string | null>(null)
  const [isFormatting, setIsFormatting] = useState(false)
  const [formatError, setFormatError] = useState(false)
  const [showFormatted, setShowFormatted] = useState(false)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [summaryError, setSummaryError] = useState<string | null>(null)

  // Build the full slug path for API call: {country}/{type}/{slug_name-case_id}
  const slugPath = country && type && slug ? `${country}/${type}/${slug}` : ''

  const { data: caseData, isLoading, error, refetch, isError } = useQuery({
    queryKey: ['case', 'slug', slugPath],
    queryFn: () => casesApi.getBySlug(slugPath),
    enabled: !!slugPath,
  })

  const hasToken = !!localStorage.getItem('token')

  const caseItem: CaseItem | undefined = caseData?.data
  const caseId = caseItem?.courtlistener_id ?? caseItem?.id ?? 0

  const { data: favoriteStatus } = useQuery({
    queryKey: ['favorite', caseId],
    queryFn: () => favoritesApi.check(caseId),
    enabled: !!caseId && hasToken,
    retry: false,
  })

  const { data: similarData } = useQuery({
    queryKey: ['similar', caseId],
    queryFn: () => casesApi.getSimilar(caseId),
    enabled: !!caseId,
  })

  // Separate mutation for auto-trigger (no conflict with manual button)
  const autoFormatMutation = useMutation({
    mutationFn: () => casesApi.formatText(caseId),
    mutationKey: ['formatTextAuto', caseId],
    onSuccess: (data) => {
      setFormattedText(data.data?.plain_text_formatted || null)
      setIsFormatting(false)
      setFormatError(false)
    },
    onError: () => {
      setIsFormatting(false)
      // Silent fail for auto-trigger - don't show error
    },
  })

  // Auto-trigger formatting when plain_text becomes available
  useEffect(() => {
    const plainText = caseItem?.plain_text
    if (plainText && plainText.length > 50 && !formattedText && !isFormatting && !autoFormatMutation.isPending) {
      autoFormatMutation.mutate()
      setIsFormatting(true)
    }
  }, [caseItem?.plain_text, formattedText, isFormatting, autoFormatMutation.isPending])

  const formatMutation = useMutation({
    mutationFn: () => casesApi.formatText(caseId),
    mutationKey: ['formatTextManual', caseId],
    onSuccess: (data) => {
      setFormattedText(data.data?.plain_text_formatted || null)
      setIsFormatting(false)
      setFormatError(false)
    },
    onError: () => {
      setIsFormatting(false)
      setFormatError(true)
    },
  })

  const handleFormatText = () => {
    if (formattedText) {
      setShowFormatted(!showFormatted)
      return
    }
    setIsFormatting(true)
    setFormatError(false)
    formatMutation.mutate()
  }

  const translateMutation = useMutation({
    mutationFn: () => casesApi.translate(caseId, translateLanguage),
    onSuccess: (data) => {
      setTranslationResult(data.data?.translated_text || '')
      setTranslationLoading(false)
      setTranslationError(null)
    },
    onError: () => {
      setTranslationLoading(false)
      setTranslationError(t('case.translateError'))
    },
  })

  const summaryMutation = useMutation({
    mutationFn: () => casesApi.summarize(caseId),
    mutationKey: ['summaryMutation', caseId],
    onSuccess: () => {
      setSummaryLoading(false)
      setSummaryError(null)
      queryClient.invalidateQueries({ queryKey: ['case', 'slug', slugPath] })
    },
    onError: () => {
      setSummaryLoading(false)
      setSummaryError(t('case.summaryError') || 'Failed to generate summary')
    },
  })

  const handleTranslate = () => {
    if (translationResult) {
      setTranslationResult(null)
      return
    }
    setTranslationError(null)
    setTranslationLoading(true)
    translateMutation.mutate()
  }

  const handleCopyTranslation = () => {
    if (translationResult) {
      navigator.clipboard.writeText(translationResult)
      setTranslationCopied(true)
      setTimeout(() => setTranslationCopied(false), 2000)
    }
  }

  const addFavoriteMutation = useMutation({
    mutationFn: () => {
      if (!caseItem) return Promise.reject()
      return favoritesApi.add(
        caseItem.courtlistener_id,
        caseItem.case_name,
        caseItem.court,
        caseItem.date_filed
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorite', caseId] })
    },
  })

  const removeFavoriteMutation = useMutation({
    mutationFn: (favoriteId: number) => favoritesApi.remove(favoriteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorite', caseId] })
    },
  })

  const handleFavorite = () => {
    if (isFavorited && favoriteId) {
      removeFavoriteMutation.mutate(favoriteId)
    } else {
      addFavoriteMutation.mutate()
    }
  }

  const handleShare = () => {
    const url = window.location.href
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const handleCreateShareLink = async () => {
    if (shareLinkCreated && shareUrl) {
      navigator.clipboard.writeText(shareUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
      return
    }
    try {
      const result = await casesApi.createShareLink(caseId)
      const url = result.data?.share_url || `${window.location.origin}/shared/${result.data?.token}`
      setShareUrl(url)
      setShareLinkCreated(true)
      navigator.clipboard.writeText(url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      handleShare()
    }
  }

  const handleExportTxt = () => {
    if (!caseItem) return
    const displayText = caseItem.plain_text || ''
    const fullText = textExpanded ? displayText : displayText.substring(0, 2000) + (displayText.length > 2000 ? '\n\n[... text truncated ...]' : '')
    const translatedText = translationResult ? `\n\n=== TRANSLATION (${translateLanguage}) ===\n${translationResult}` : ''

    const content = [
      `Case: ${caseItem.case_name}`,
      `Court: ${caseItem.court || 'N/A'}`,
      `Date Filed: ${caseItem.date_filed ? new Date(caseItem.date_filed).toLocaleDateString() : 'N/A'}`,
      `Citation: ${caseItem.citation || 'N/A'}`,
      `Docket: ${caseItem.docket_number || 'N/A'}`,
      '',
      `=== AI SUMMARY ===`,
      caseItem.summary || 'N/A',
      '',
      `=== CASE TEXT ===`,
      fullText,
      '',
      translatedText,
      '',
      `Source: ${caseItem.source_url || `https://www.courtlistener.com/case/${caseId}/`}`,
    ].join('\n')

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    const slugName = caseItem.case_name.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, '_').substring(0, 50)
    a.href = url
    a.download = `${slugName}_${caseId}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleSimilarCaseClick = (sc: SimilarCase) => {
    // Prefer slug URL if available, fall back to numeric ID
    if (sc.slug_url) {
      navigate(sc.slug_url)
    } else {
      navigate(`/cases/${sc.id}`)
    }
  }

  const isFavorited = favoriteStatus?.data?.is_favorited || false
  const favoriteId = favoriteStatus?.data?.favorite_id || null
  const similarCases: SimilarCase[] = similarData?.data?.similar_cases || []

  const errorMessage = (error as any)?.response?.data?.detail
    || (error as any)?.response?.data?.message
    || (error as any)?.response?.statusText
    || (error as any)?.message
    || String(error) || ''

  const TEXT_PREVIEW_LENGTH = 2000
  const displayText = caseItem?.plain_text || ''
  const needsTruncation = displayText.length > TEXT_PREVIEW_LENGTH
  const textToShow = textExpanded || !needsTruncation ? displayText : displayText.substring(0, TEXT_PREVIEW_LENGTH)

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 border-b border-gray-100 dark:border-gray-700/50 sticky top-0 z-50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors text-sm"
            >
              <ArrowLeft className="h-4 w-4" />
              {t('common.back')}
            </button>
            <div className="h-5 w-px bg-gray-200 dark:bg-gray-700" />
            <button onClick={() => navigate('/')} className="flex items-center gap-2 group">
              <div className="w-7 h-7 rounded-lg bg-primary-600 dark:bg-primary-500 flex items-center justify-center group-hover:bg-primary-700 dark:group-hover:bg-primary-600 transition-colors">
                <FileText className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="font-serif text-lg font-bold text-gray-900 dark:text-white hidden sm:block">{t('common.brand')}</span>
            </button>
          </div>
          <div className="flex items-center gap-1 sm:gap-2">
            <ThemeSwitcher />
            <LanguageSwitcher />
            <div className="h-5 w-px bg-gray-200 dark:bg-gray-700 hidden sm:block" />
            <button
              onClick={handleFavorite}
              disabled={addFavoriteMutation.isPending || removeFavoriteMutation.isPending}
              className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all text-sm ${
                isFavorited
                  ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 hover:bg-yellow-100 dark:hover:bg-yellow-900/30'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <Star className="h-4 w-4" fill={isFavorited ? 'currentColor' : 'none'} />
              <span className="hidden md:inline">{isFavorited ? t('case.removeFavorite') : t('case.addFavorite')}</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Loading skeleton */}
        {isLoading && <CaseSkeleton />}

        {/* Error display */}
        {isError && !isLoading && (
          <ErrorDisplay
            message={errorMessage}
            onRetry={() => refetch()}
          />
        )}

        {/* Content */}
        {!isLoading && !isError && caseItem && (
          <div className="space-y-5">
            {/* Case Header */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 sm:p-8 border border-gray-100 dark:border-gray-700 transition-colors duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-1 h-16 bg-primary-500 dark:bg-primary-400 rounded-full mt-1" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 flex-wrap">
                    <h1 className="text-2xl sm:text-3xl font-serif font-bold text-gray-900 dark:text-white leading-tight">
                      {caseItem.case_name}
                    </h1>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {caseItem.source_url && (
                        <a
                          href={caseItem.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 hover:text-primary-700 dark:hover:text-primary-300 border border-gray-200 dark:border-gray-600 hover:border-primary-200 dark:hover:border-primary-700 transition-all"
                        >
                          <ExternalLink className="h-3.5 w-3.5" />
                          {t('case.viewOriginal')}
                        </a>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-5 mt-3 text-sm text-gray-500 dark:text-gray-400">
                    {caseItem.court && (
                      <div className="flex items-center gap-1.5">
                        <MapPin className="h-4 w-4" />
                        {caseItem.court}
                      </div>
                    )}
                    {caseItem.date_filed && (
                      <div className="flex items-center gap-1.5">
                        <Calendar className="h-4 w-4" />
                        {t('case.filed')}: {new Date(caseItem.date_filed).toLocaleDateString()}
                      </div>
                    )}
                    {caseItem.citation && (
                      <div className="flex items-center gap-1.5 font-mono text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">
                        <FileText className="h-3.5 w-3.5" />
                        {caseItem.citation}
                      </div>
                    )}
                  </div>

                  {caseItem.docket_number && (
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 font-mono">
                      {t('case.docket')}: {caseItem.docket_number}
                    </p>
                  )}

                  {/* Keywords */}
                  {caseItem.keywords && caseItem.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-4">
                      {caseItem.keywords.slice(0, 10).map((kw) => (
                        <span
                          key={kw}
                          className="px-2.5 py-0.5 text-xs font-medium bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full border border-primary-100 dark:border-primary-800/40"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Action Bar */}
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={handleFavorite}
                disabled={addFavoriteMutation.isPending || removeFavoriteMutation.isPending}
                className={`sm:hidden flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all text-sm ${
                  isFavorited
                    ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Star className="h-4 w-4" fill={isFavorited ? 'currentColor' : 'none'} />
              </button>

              <button
                onClick={handleExportTxt}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 hover:text-emerald-700 dark:hover:text-emerald-300 border border-gray-200 dark:border-gray-700 hover:border-emerald-200 dark:hover:border-emerald-800/40 transition-all"
              >
                <Download className="h-4 w-4" />
                {t('case.exportTxt')}
              </button>

              <button
                onClick={handleCreateShareLink}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-violet-50 dark:hover:bg-violet-900/20 hover:text-violet-700 dark:hover:text-violet-300 border border-gray-200 dark:border-gray-700 hover:border-violet-200 dark:hover:border-violet-800/40 transition-all"
              >
                <Link2 className="h-4 w-4" />
                {shareLinkCreated ? t('case.copyLink') : t('case.shareLink')}
              </button>

              {copied && (
                <span className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1 animate-fade-in">
                  <Check className="h-3.5 w-3.5" /> {t('case.copied')}
                </span>
              )}
            </div>

            {/* AI Summary */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 sm:p-8 border border-gray-100 dark:border-gray-700 transition-colors duration-300 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{t('case.summary')}</h2>
                {caseItem.summary && (
                  <span className="text-xs text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-2 py-0.5 rounded-full font-medium">{t('case.aiGenerated')}</span>
                )}
              </div>
              {caseItem.summary ? (
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{caseItem.summary}</p>
              ) : (
                <div className="text-center py-4">
                  <p className="text-gray-500 dark:text-gray-400 mb-3 text-sm">{t('case.aiPowered')}</p>
                  <button
                    onClick={() => {
                      setSummaryLoading(true)
                      setSummaryError(null)
                      summaryMutation.mutate()
                    }}
                    disabled={summaryLoading}
                    className="px-4 py-2 bg-primary-600 dark:bg-primary-500 text-white rounded-xl hover:bg-primary-700 dark:hover:bg-primary-600 transition-colors text-sm font-medium disabled:opacity-60 flex items-center gap-2 mx-auto"
                  >
                    {summaryLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {t('case.generatingSummary')}
                      </>
                    ) : (
                      t('case.generate')
                    )}
                  </button>
                  {summaryError && (
                    <p className="text-xs text-red-500 mt-2">{summaryError}</p>
                  )}
                </div>
              )}
            </div>

            {/* Translation Panel */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 sm:p-8 border border-gray-100 dark:border-gray-700 transition-colors duration-300 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Languages className="h-5 w-5 text-primary-500" />
                  {t('case.translationLabel')}
                </h2>
              </div>
              <div className="flex items-center gap-3 flex-wrap">
                <select
                  value={translateLanguage}
                  onChange={(e) => setTranslateLanguage(e.target.value)}
                  className="px-3 py-2 rounded-lg text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-400 dark:focus:ring-primary-500 cursor-pointer"
                >
                  {TRANSLATION_LANGUAGES.map((lang) => (
                    <option key={lang.value} value={lang.value}>{lang.label}</option>
                  ))}
                </select>
                <button
                  onClick={handleTranslate}
                  disabled={translationLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 dark:bg-primary-500 text-white rounded-xl hover:bg-primary-700 dark:hover:bg-primary-600 transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {translationLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : translationResult ? (
                    <>
                      <XCircle className="h-4 w-4" />
                      {t('case.hideTranslation')}
                    </>
                  ) : (
                    <>
                      <Languages className="h-4 w-4" />
                      {t('case.translateBtn') || 'Translate'}
                    </>
                  )}
                </button>
                {translationResult && (
                  <button
                    onClick={handleCopyTranslation}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                  >
                    {translationCopied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                    {translationCopied ? t('case.copyTranslation') : t('case.copy')}
                  </button>
                )}
              </div>

              {translationResult && (
                <div className="mt-4 p-4 bg-primary-50 dark:bg-primary-900/20 border border-primary-100 dark:border-primary-800/40 rounded-xl">
                  <p className="text-sm text-primary-800 dark:text-primary-200 mb-2 font-medium">
                    {translateLanguage} {t('case.translationLabel')}
                  </p>
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">{translationResult}</p>
                </div>
              )}

              {translationError && (
                <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/40 rounded-xl flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-500 dark:text-red-400 flex-shrink-0" />
                  <p className="text-sm text-red-700 dark:text-red-300">{translationError}</p>
                </div>
              )}
            </div>

            {/* Entities */}
            {caseItem.entities && Object.keys(caseItem.entities).length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 sm:p-8 border border-gray-100 dark:border-gray-700 transition-colors duration-300 shadow-sm">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{t('case.keyEntities')}</h2>
                <div className="space-y-3">
                  {Object.entries(caseItem.entities).map(([type, entities]) => (
                    <div key={type}>
                      <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2">{type}</h3>
                      <div className="flex flex-wrap gap-1.5">
                        {(entities as string[]).map((entity) => (
                          <span
                            key={entity}
                            className="px-3 py-1 text-sm bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full font-medium border border-primary-100 dark:border-primary-800/40"
                          >
                            {entity}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Full Text */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 sm:p-8 border border-gray-100 dark:border-gray-700 transition-colors duration-300 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{t('case.fullText')}</h2>
                <div className="flex items-center gap-2">
                  {displayText && displayText.length > 50 && (
                    <button
                      onClick={handleFormatText}
                      disabled={isFormatting}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-primary-900/50 border border-primary-200 dark:border-primary-800/40 transition-all disabled:opacity-50"
                    >
                      {isFormatting ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <FileText className="h-3.5 w-3.5" />
                      )}
                      {formattedText
                        ? (showFormatted ? t('case.showOriginal') : t('case.showFormatted'))
                        : isFormatting
                        ? t('case.formatting')
                        : t('case.aiFormat')}
                    </button>
                  )}
                  {needsTruncation && (
                    <button
                      onClick={() => setTextExpanded(!textExpanded)}
                      className="flex items-center gap-1.5 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium transition-colors"
                    >
                      {textExpanded ? (
                        <>
                          <ChevronUp className="h-4 w-4" />
                          {t('case.showLess')}
                        </>
                      ) : (
                        <>
                          <ChevronDown className="h-4 w-4" />
                          {t('case.viewMore')} ({displayText.length.toLocaleString()} {t('case.chars')})
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
              {formatError && (
                <div className="mb-3 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/40 rounded-lg">
                  <p className="text-xs text-red-600 dark:text-red-400">{t('case.formatError')}</p>
                </div>
              )}
              {displayText ? (
                <div className="prose max-w-none">
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap font-mono text-sm bg-gray-50 dark:bg-gray-900 p-4 rounded-lg border border-gray-100 dark:border-gray-700">
                    {showFormatted && formattedText
                      ? formattedText
                      : textToShow}
                  </p>
                  {formattedText && displayText.length > textToShow.length && !textExpanded && (
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 text-center">
                      {t('case.formattedVersion')}
                    </p>
                  )}
                </div>
              ) : (
                <div className="text-center py-6">
                  <p className="text-gray-500 dark:text-gray-400 mb-2">{t('case.fullTextUnavailable')}</p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-4">{t('case.textUnavailableReason')}</p>
                  {caseItem?.source_url && (
                    <a
                      href={caseItem.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 hover:bg-primary-100 dark:hover:bg-primary-900/30 border border-primary-200 dark:border-primary-800/40 transition-colors"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                      {t('case.viewSource')}
                    </a>
                  )}
                </div>
              )}
            </div>

            {/* Similar Cases */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 sm:p-8 border border-gray-100 dark:border-gray-700 transition-colors duration-300 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{t('case.similar')}</h2>
              {similarCases.length > 0 ? (
                <div className="space-y-2">
                  {similarCases.map((sc) => (
                    <div
                      key={sc.id}
                      className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition cursor-pointer border border-transparent hover:border-gray-200 dark:hover:border-gray-600"
                      onClick={() => handleSimilarCaseClick(sc)}
                    >
                      <div>
                        <h3 className="text-primary-600 dark:text-primary-400 font-medium hover:underline text-sm">
                          {sc.case_name}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          {sc.court || t('common.noData')} &middot; {sc.date_filed ? new Date(sc.date_filed).toLocaleDateString() : t('common.noData')}
                        </p>
                      </div>
                      <span className="text-xs font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-2 py-1 rounded-full">
                        {(sc.similarity * 100).toFixed(0)}{t('case.match')}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6">
                  <p className="text-gray-500 dark:text-gray-400 mb-3 text-sm">{t('case.noSimilar')}</p>
                  <button
                    onClick={() => casesApi.getSimilar(caseId)}
                    className="text-primary-600 dark:text-primary-400 hover:underline font-medium text-sm"
                  >
                    {t('case.findSimilar')} &rarr;
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  )
}
