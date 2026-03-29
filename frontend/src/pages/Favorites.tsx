import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Star, Trash2, FileText, Calendar, MapPin, Loader2, Scale } from 'lucide-react'
import { Link } from 'react-router-dom'
import { favoritesApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'

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
  const { t, language } = useI18n()
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
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
      return new Date(dateStr).toLocaleDateString(language === 'zh' ? 'zh-CN' : 'en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    } catch {
      return dateStr
    }
  }

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
              to="/account"
              className="hidden sm:flex items-center px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
            >
              {t('nav.account')}
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-10">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-bold text-[var(--text-primary)] mb-2">
            {t('favorites.title')}
          </h1>
          <p className="text-[var(--text-secondary)]">
            {t('favorites.total')}: {total}
          </p>
        </div>

        {/* Loading */}
        {isLoading && (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="h-8 w-8 animate-spin text-[var(--brand-primary)]" />
            <span className="ml-3 text-[var(--text-secondary)]">{t('common.loading')}</span>
          </div>
        )}

        {/* Error */}
        {isError && (
          <div className="card text-center py-12">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4" style={{ background: 'var(--status-error-bg)' }}>
              <Star className="h-6 w-6" style={{ color: 'var(--status-error)' }} />
            </div>
            <p className="text-[var(--text-secondary)]">{t('common.loadingFailed')}</p>
          </div>
        )}

        {/* Empty */}
        {!isLoading && !isError && favorites.length === 0 && (
          <div className="card text-center py-16">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-5" style={{ background: 'var(--bg-tertiary)' }}>
              <Star className="h-7 w-7 text-[var(--text-tertiary)]" />
            </div>
            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{t('favorites.empty')}</h3>
            <p className="text-[var(--text-secondary)] mb-6 text-sm max-w-sm mx-auto">{t('favorites.emptyDesc')}</p>
            <button
              onClick={() => navigate('/search')}
              className="btn-primary"
            >
              {t('favorites.browse')}
            </button>
          </div>
        )}

        {/* List */}
        {!isLoading && !isError && favorites.length > 0 && (
          <div className="space-y-4">
            {favorites.map((item) => (
              <div
                key={item.id}
                className="card hover:shadow-md cursor-pointer group"
                onClick={() => navigate(`/cases/${item.case_id}`)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold text-[var(--brand-primary)] group-hover:underline mb-2 truncate">
                      {item.case_name}
                    </h3>
                    <div className="flex flex-wrap gap-x-5 gap-y-1.5 text-sm text-[var(--text-tertiary)]">
                      {item.court && (
                        <div className="flex items-center gap-1.5">
                          <MapPin className="h-3.5 w-3.5" />
                          <span className="truncate max-w-[200px]">{item.court}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-1.5">
                        <Calendar className="h-3.5 w-3.5" />
                        {formatDate(item.date_filed)}
                      </div>
                      <div className="flex items-center gap-1.5 font-mono text-xs px-2 py-0.5 rounded" style={{ background: 'var(--bg-tertiary)' }}>
                        <FileText className="h-3.5 w-3.5" />
                        #{item.case_id}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        if (window.confirm(t('favorites.removeConfirm'))) {
                          deleteMutation.mutate(item.id)
                        }
                      }}
                      className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--status-error)] hover:bg-[var(--status-error-bg)] transition-all"
                      title={t('favorites.remove')}
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                    <span className="text-xs font-medium text-[var(--brand-primary)] hover:underline hidden sm:inline">
                      {t('case.viewDetails')}
                    </span>
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
