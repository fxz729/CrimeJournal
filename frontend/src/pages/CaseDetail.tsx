import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, FileText, Calendar, MapPin, Loader2, Star, Share2, Link2, Check } from 'lucide-react'
import { casesApi, favoritesApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'

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
  html_text: string
  summary: string
  keywords: string[]
  entities: Record<string, string[]>
}

interface SimilarCase {
  id: number
  case_name: string
  court: string
  date_filed: string
  similarity: number
}

export default function CaseDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { t } = useI18n()
  const queryClient = useQueryClient()
  const caseId = Number(id)

  const [copied, setCopied] = useState(false)

  const { data: caseData, isLoading, error, refetch } = useQuery({
    queryKey: ['case', id],
    queryFn: () => casesApi.getById(caseId),
    enabled: !!id,
  })

  const { data: favoriteStatus } = useQuery({
    queryKey: ['favorite', caseId],
    queryFn: () => favoritesApi.check(caseId),
    enabled: !!id,
    retry: false,
  })

  const { data: similarData } = useQuery({
    queryKey: ['similar', caseId],
    queryFn: () => casesApi.getSimilar(caseId),
    enabled: !!id,
  })

  const addFavoriteMutation = useMutation({
    mutationFn: () => {
      const caseItem = caseData?.data
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

  const caseItem: CaseItem | undefined = caseData?.data
  const isFavorited = favoriteStatus?.data?.is_favorited || false
  const favoriteId = favoriteStatus?.data?.favorite_id || null
  const similarCases: SimilarCase[] = similarData?.data?.similar_cases || []

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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-5 w-5" />
              {t('common.back')}
            </button>
            <div className="flex items-center gap-2">
              <FileText className="h-6 w-6 text-primary-600" />
              <span className="font-serif text-xl font-bold">CrimeJournal</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <button
              onClick={handleFavorite}
              disabled={addFavoriteMutation.isPending || removeFavoriteMutation.isPending}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition ${
                isFavorited
                  ? 'text-yellow-500 bg-yellow-50 hover:bg-yellow-100'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Star className="h-5 w-5" fill={isFavorited ? 'currentColor' : 'none'} />
              {isFavorited ? t('case.removeFavorite') : t('case.addFavorite')}
            </button>
            <button
              onClick={handleShare}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 px-3 py-1.5 rounded-lg hover:bg-gray-100 transition"
            >
              {copied ? (
                <>
                  <Check className="h-5 w-5 text-green-500" />
                  {t('case.shareSuccess')}
                </>
              ) : (
                <>
                  <Share2 className="h-5 w-5" />
                  {t('common.share')}
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {isLoading && (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            <span className="ml-3 text-gray-600">{t('common.loading')}</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
            <FileText className="h-5 w-5" />
            <span>{t('common.error')}</span>
            <button
              onClick={() => refetch()}
              className="ml-auto text-sm underline hover:no-underline"
            >
              {t('common.retry')}
            </button>
          </div>
        )}

        {caseItem && (
          <div className="space-y-6">
            {/* Case Header */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h1 className="text-3xl font-serif font-bold mb-4">
                {caseItem.case_name}
              </h1>

              <div className="flex flex-wrap gap-6 text-gray-600 mb-6">
                <div className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  {caseItem.court || t('common.noData')}
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  {t('case.filed')}: {caseItem.date_filed ? new Date(caseItem.date_filed).toLocaleDateString() : t('common.noData')}
                </div>
                {caseItem.citation && (
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    {caseItem.citation}
                  </div>
                )}
              </div>

              {caseItem.docket_number && (
                <p className="text-sm text-gray-500">
                  {t('case.docket')}: {caseItem.docket_number}
                </p>
              )}

              {/* Keywords */}
              {caseItem.keywords && caseItem.keywords.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {caseItem.keywords.slice(0, 8).map((kw) => (
                    <span
                      key={kw}
                      className="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded-full"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* AI Summary */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-xl font-semibold mb-4">{t('case.summary')}</h2>
              {caseItem.summary ? (
                <p className="text-gray-700 leading-relaxed">{caseItem.summary}</p>
              ) : (
                <div>
                  <p className="text-gray-500 mb-4">{t('case.aiPowered')}</p>
                  <button
                    onClick={() => casesApi.summarize(caseId)}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
                  >
                    {t('case.generate')}
                  </button>
                </div>
              )}
            </div>

            {/* Entities */}
            {caseItem.entities && Object.keys(caseItem.entities).length > 0 && (
              <div className="bg-white rounded-xl shadow-sm p-8">
                <h2 className="text-xl font-semibold mb-4">{t('case.keyEntities')}</h2>
                <div className="space-y-4">
                  {Object.entries(caseItem.entities).map(([type, entities]) => (
                    <div key={type}>
                      <h3 className="text-sm font-medium text-gray-500 mb-2">{type}</h3>
                      <div className="flex flex-wrap gap-2">
                        {(entities as string[]).map((entity) => (
                          <span
                            key={entity}
                            className="px-3 py-1 text-sm bg-primary-50 text-primary-700 rounded-full"
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
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-xl font-semibold mb-4">{t('case.fullText')}</h2>
              {caseItem.plain_text ? (
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {caseItem.plain_text.substring(0, 2000)}
                    {caseItem.plain_text.length > 2000 && '...'}
                  </p>
                </div>
              ) : (
                <p className="text-gray-500">{t('case.fullTextUnavailable')}</p>
              )}
            </div>

            {/* Similar Cases */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-xl font-semibold mb-4">{t('case.similar')}</h2>
              {similarCases.length > 0 ? (
                <div className="space-y-3">
                  {similarCases.map((sc) => (
                    <div
                      key={sc.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition cursor-pointer"
                      onClick={() => navigate(`/cases/${sc.id}`)}
                    >
                      <div>
                        <h3 className="text-primary-600 font-medium hover:underline">
                          {sc.case_name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {sc.court || t('common.noData')} &middot; {sc.date_filed ? new Date(sc.date_filed).toLocaleDateString() : t('common.noData')}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-medium text-primary-600">
                          {t('case.similarity')}: {(sc.similarity * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6">
                  <p className="text-gray-500 mb-4">{t('case.noSimilar')}</p>
                  <button
                    onClick={() => casesApi.getSimilar(caseId)}
                    className="text-primary-600 hover:underline font-medium"
                  >
                    {t('case.findSimilar')} &rarr;
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
