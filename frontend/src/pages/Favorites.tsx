import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Star, Trash2, FileText, Calendar, MapPin, Loader2, AlertCircle } from 'lucide-react'
import { favoritesApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { useAuth } from '../lib/auth'

interface FavoriteItem {
  id: number
  case_id: number
  case_name: string
  court: string | null
  date_filed: string | null
  created_at: string
}

export default function Favorites() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['favorites'],
    queryFn: () => favoritesApi.getAll(),
  })

  const deleteMutation = useMutation({
    mutationFn: (favoriteId: number) => favoritesApi.remove(favoriteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] })
    },
  })

  const favorites: FavoriteItem[] = data?.data?.items || []
  const total = data?.data?.total || 0

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return t('common.noData')
    try {
      return new Date(dateStr).toLocaleDateString()
    } catch {
      return dateStr
    }
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
              <Star className="h-5 w-5" />
              <span className="font-serif text-xl font-bold">CrimeJournal</span>
            </button>
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
              onClick={() => navigate('/account')}
              className="text-gray-600 hover:text-gray-900"
            >
              {t('nav.account')}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-bold text-gray-900 mb-2">
            {t('favorites.title')}
          </h1>
          <p className="text-gray-600">
            {t('favorites.total')}: {total}
          </p>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            <span className="ml-3 text-gray-600">{t('common.loading')}</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            <span>{t('common.loadingFailed')}</span>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && favorites.length === 0 && (
          <div className="bg-white rounded-xl p-12 text-center shadow-sm">
            <Star className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">{t('favorites.empty')}</h3>
            <p className="text-gray-600 mb-6">{t('favorites.emptyDesc')}</p>
            <button
              onClick={() => navigate('/search')}
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
            >
              {t('favorites.browse')}
            </button>
          </div>
        )}

        {/* Favorites List */}
        {!isLoading && !error && favorites.length > 0 && (
          <div className="space-y-4">
            {favorites.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition cursor-pointer"
                onClick={() => navigate(`/cases/${item.case_id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-primary-600 hover:underline mb-2">
                      {item.case_name}
                    </h3>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        {item.court || t('common.noData')}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(item.date_filed)}
                      </div>
                      <div className="flex items-center gap-1">
                        <FileText className="h-4 w-4" />
                        {item.case_id}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        if (window.confirm(t('favorites.removeConfirm'))) {
                          deleteMutation.mutate(item.id)
                        }
                      }}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                      title={t('favorites.remove')}
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                    <button className="text-primary-600 hover:underline text-sm font-medium">
                      {t('case.viewDetails')}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
