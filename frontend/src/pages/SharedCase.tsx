import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Scale, FileText, Calendar, MapPin, Loader2, AlertCircle, ArrowRight } from 'lucide-react'
import { casesApi } from '../lib/api'
import { useI18n } from '../lib/i18n'

interface SharedCaseData {
  case_name: string
  court?: string
  date_filed?: string
  citation?: string
  summary?: string
}

export default function SharedCase() {
  const { token } = useParams<{ token: string }>()
  const { t } = useI18n()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['shared', token],
    queryFn: () => casesApi.getSharedCase(token!),
    enabled: !!token,
  })

  const caseData: SharedCaseData | undefined = data?.data

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-slate-900 dark:to-indigo-950 transition-colors duration-300">
      {/* Minimal header - logo only */}
      <div className="px-6 py-5">
        <Link to="/" className="flex items-center gap-2.5 group inline-flex">
          <div className="w-9 h-9 rounded-xl bg-primary-600 dark:bg-primary-500 flex items-center justify-center shadow-md shadow-primary-500/20">
            <Scale className="h-5 w-5 text-white" />
          </div>
          <span className="font-serif text-xl font-bold text-gray-900 dark:text-white">{t('common.brand')}</span>
        </Link>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-6 pb-16">
        {/* Public badge */}
        <div className="flex items-center gap-2 mb-8">
          <div className="px-3 py-1.5 rounded-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700 shadow-sm text-xs font-medium text-gray-600 dark:text-gray-400">
            {t('shared.publicPreview')}
          </div>
          <span className="text-xs text-gray-400 dark:text-gray-500">{t('shared.signInPrompt')}</span>
        </div>

        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary-500 mb-4" />
            <p className="text-gray-500 dark:text-gray-400 text-sm">{t('shared.loading')}</p>
          </div>
        )}

        {isError && (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-red-50 dark:bg-red-900/20 flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="h-8 w-8 text-red-500" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              {t('case.shareLinkExpired')}
            </h2>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-6">
              {t('shared.linkExpired')}
            </p>
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 dark:bg-primary-500 text-white rounded-xl hover:bg-primary-700 dark:hover:bg-primary-600 transition-colors font-medium"
            >
              {t('shared.signUpForAccess')}
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        )}

        {caseData && (
          <div className="space-y-5">
            {/* Case Card */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl p-8 border border-gray-200/60 dark:border-gray-700/60 shadow-xl shadow-gray-900/5 dark:shadow-black/20">
              {/* Header */}
              <div className="flex items-start gap-4 mb-6">
                <div className="flex-shrink-0 w-1.5 h-14 bg-primary-500 dark:bg-primary-400 rounded-full" />
                <div>
                  <h1 className="text-2xl sm:text-3xl font-serif font-bold text-gray-900 dark:text-white leading-tight">
                    {caseData.case_name}
                  </h1>
                  <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-500 dark:text-gray-400">
                    {caseData.court && (
                      <div className="flex items-center gap-1.5">
                        <MapPin className="h-4 w-4" />
                        {caseData.court}
                      </div>
                    )}
                    {caseData.date_filed && (
                      <div className="flex items-center gap-1.5">
                        <Calendar className="h-4 w-4" />
                        {new Date(caseData.date_filed).toLocaleDateString()}
                      </div>
                    )}
                    {caseData.citation && (
                      <div className="flex items-center gap-1.5 font-mono text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">
                        <FileText className="h-3.5 w-3.5" />
                        {caseData.citation}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Summary */}
              {caseData.summary && (
                <div className="p-4 bg-primary-50/70 dark:bg-primary-900/20 rounded-xl border border-primary-100/60 dark:border-primary-800/40 mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-5 h-5 rounded-md bg-primary-500 flex items-center justify-center">
                      <Scale className="h-3 w-3 text-white" />
                    </div>
                    <span className="text-xs font-bold text-primary-700 dark:text-primary-300 uppercase tracking-wider">{t('shared.aiSummary')}</span>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{caseData.summary}</p>
                </div>
              )}

              {/* Preview notice */}
              <div className="text-center py-4 border-t border-gray-100 dark:border-gray-700">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                  {t('shared.previewPrompt')}
                </p>
                <div className="flex items-center justify-center gap-3">
                  <Link
                    to="/login"
                    className="px-5 py-2.5 bg-primary-600 dark:bg-primary-500 text-white rounded-xl hover:bg-primary-700 dark:hover:bg-primary-600 transition-colors text-sm font-medium shadow-md shadow-primary-500/20"
                  >
                    {t('shared.signIn')}
                  </Link>
                  <Link
                    to="/register"
                    className="px-5 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
                  >
                    {t('shared.signUp')}
                  </Link>
                </div>
              </div>
            </div>

            {/* Features preview */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: t('shared.featureFullText'), icon: '📄' },
                { label: t('shared.featureTranslation'), icon: '🌐' },
                { label: t('shared.featureEntities'), icon: '🏷️' },
              ].map((feature) => (
                <div key={feature.label} className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-3 text-center border border-gray-200/40 dark:border-gray-700/40">
                  <div className="text-2xl mb-1">{feature.icon}</div>
                  <p className="text-xs font-medium text-gray-600 dark:text-gray-400">{feature.label}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="absolute bottom-6 left-0 right-0 text-center">
        <p className="text-xs text-gray-400 dark:text-gray-500">
          {t('footer.tagline')}
        </p>
      </div>
    </div>
  )
}
