import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, FileText, Calendar, MapPin, Loader2, Star, Share2 } from 'lucide-react'
import { casesApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'

export default function CaseDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { t } = useI18n()

  const { data: caseData, isLoading, error } = useQuery({
    queryKey: ['case', id],
    queryFn: () => casesApi.getById(Number(id)),
    enabled: !!id,
  })

  const caseItem = caseData?.data

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
            <button className="text-gray-600 hover:text-gray-900 flex items-center gap-2">
              <Star className="h-5 w-5" />
              {t('common.save')}
            </button>
            <button className="text-gray-600 hover:text-gray-900 flex items-center gap-2">
              <Share2 className="h-5 w-5" />
              {t('common.share')}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {isLoading && (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg">
            {t('common.error')}
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
                  {caseItem.court || 'Unknown Court'}
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  {t('case.filed')}: {caseItem.date_filed ? new Date(caseItem.date_filed).toLocaleDateString() : 'Unknown'}
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
            </div>

            {/* AI Summary */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-xl font-semibold mb-4">{t('case.summary')}</h2>
              {caseItem.summary ? (
                <p className="text-gray-700 leading-relaxed">{caseItem.summary}</p>
              ) : (
                <div>
                  <p className="text-gray-500 mb-4">
                    Get an AI-generated summary powered by MiniMax.
                  </p>
                  <button
                    onClick={() => casesApi.summarize(Number(id))}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
                  >
                    {t('case.generate')}
                  </button>
                </div>
              )}
            </div>

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
                <p className="text-gray-500">Full text not available.</p>
              )}
            </div>

            {/* Similar Cases */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-xl font-semibold mb-4">{t('case.similar')}</h2>
              <button
                onClick={() => casesApi.getSimilar(Number(id))}
                className="text-primary-600 hover:underline"
              >
                Find Similar Cases &rarr;
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
