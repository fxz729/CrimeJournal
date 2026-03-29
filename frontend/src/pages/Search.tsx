import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import {
  Search as SearchIcon, Loader2, FileText, File, Calendar,
  ChevronLeft, ChevronRight, Sparkles, Scale, ArrowRight,
  History, Trash2, ChevronRight as ChevronRightIcon, X, SlidersHorizontal
} from 'lucide-react'
import { casesApi, historyApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'
import { useAuth } from '../lib/auth'

interface CaseResult {
  id: number
  courtlistener_id?: number
  case_name: string
  court: string
  date_filed: string
  citation: string
  docket_number: string
  slug?: string
  slug_url?: string
  has_text?: boolean
}

interface HistoryItem {
  id: number
  query: string
  timestamp: string
  result_count?: number
}

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [court, setCourt] = useState(searchParams.get('court') || '')
  const [dateMin, setDateMin] = useState(searchParams.get('date_min') || '')
  const [dateMax, setDateMax] = useState(searchParams.get('date_max') || '')
  const [caseType, setCaseType] = useState(searchParams.get('case_type') || '')
  const [courtLevel, setCourtLevel] = useState(searchParams.get('court_level') || '')
  const [minCitations, setMinCitations] = useState(searchParams.get('min_citations') || '')
  const [hasText, setHasText] = useState<string>(searchParams.get('has_text') || '')
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1)
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)
  const navigate = useNavigate()
  const { t, language } = useI18n()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  // Sync state to URL when it changes
  useEffect(() => {
    const params = new URLSearchParams()
    if (query) params.set('q', query)
    if (court) params.set('court', court)
    if (dateMin) params.set('date_min', dateMin)
    if (dateMax) params.set('date_max', dateMax)
    if (caseType) params.set('case_type', caseType)
    if (courtLevel) params.set('court_level', courtLevel)
    if (minCitations) params.set('min_citations', minCitations)
    if (hasText) params.set('has_text', hasText)
    if (page > 1) params.set('page', String(page))
    setSearchParams(params, { replace: true })
  }, [query, court, dateMin, dateMax, caseType, courtLevel, minCitations, hasText, page, setSearchParams])

  const filters: Record<string, string> = {}
  if (court) filters.court = court
  if (dateMin) filters.date_min = dateMin
  if (dateMax) filters.date_max = dateMax
  if (caseType) filters.case_type = caseType
  if (courtLevel) filters.court_level = courtLevel
  if (minCitations) filters.min_citations = minCitations
  if (hasText) filters.has_text = hasText

  const { data, isLoading, error } = useQuery({
    queryKey: ['search', query, court, dateMin, dateMax, caseType, courtLevel, minCitations, hasText, page],
    queryFn: () => casesApi.search(query, page, filters),
    enabled: query.length > 2,
  })

  // Search history
  const { data: historyData } = useQuery({
    queryKey: ['history'],
    queryFn: () => historyApi.getAll(),
    enabled: !!user,
  })
  const historyItems: HistoryItem[] = historyData?.data?.history || historyData?.data?.results || []

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
  }

  const handleQueryChange = (value: string) => {
    setQuery(value)
    setPage(1)
  }

  const handleHistoryClick = (item: HistoryItem) => {
    setQuery(item.query)
    setPage(1)
  }

  const deleteHistoryMutation = useMutation({
    mutationFn: (id: number) => historyApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['history'] }),
  })

  const clearAllHistoryMutation = useMutation({
    mutationFn: () => historyApi.clearAll(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] })
    },
  })

  const clearFilters = () => {
    setCourt('')
    setDateMin('')
    setDateMax('')
    setCaseType('')
    setCourtLevel('')
    setMinCitations('')
    setHasText('')
    setPage(1)
  }

  const hasFilters = !!(court || dateMin || dateMax || caseType || courtLevel || minCitations || hasText)
  const results = data?.data?.results || []
  const totalResults = data?.data?.total || 0
  const totalPages = data?.data?.total_pages || 1
  const currentPage = data?.data?.page || page
  const perPage = 20
  const from = totalResults > 0 ? (currentPage - 1) * perPage + 1 : 0
  const to = Math.min(currentPage * perPage, totalResults)

  return (
    <div className="min-h-screen bg-[var(--bg-secondary)] transition-colors duration-300">
      {/* Header */}
      <header className="bg-[var(--bg-primary)]/80 border-b border-[var(--border-default)] sticky top-0 z-50 backdrop-blur-md header-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center group-hover:bg-primary-600 transition-colors shadow-sm">
              <Scale className="h-4 w-4 text-white" />
            </div>
            <span className="font-serif text-lg font-bold text-[var(--text-primary)] hidden sm:block">CrimeJournal</span>
          </button>
          <div className="flex items-center gap-1 sm:gap-3">
            <ThemeSwitcher />
            <LanguageSwitcher />
            <div className="h-5 w-px bg-[var(--border-default)] hidden sm:block" />
            <button
              onClick={() => navigate(user ? '/favorites' : '/login')}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
            >
              <FileText className="h-4 w-4" />
              {t('nav.favorites')}
            </button>
            <button
              onClick={() => navigate(user ? '/account' : '/login')}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
            >
              {t('nav.account')}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex gap-6">
          {/* Search History Sidebar */}
          {user && (
            <div className={`${historyOpen ? 'w-64 flex-shrink-0' : 'w-0'} transition-all duration-300 overflow-hidden`}>
              <div className="w-64">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
                    <History className="h-4 w-4" />
                    {t('search.recentSearches')}
                  </h3>
                  <div className="flex items-center gap-1">
                    {historyItems.length > 0 && (
                      <button
                        onClick={() => clearAllHistoryMutation.mutate()}
                        disabled={clearAllHistoryMutation.isPending}
                        className="p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-xs text-red-500 hover:text-red-600 dark:hover:text-red-400 font-medium"
                        title={t('search.clearAll')}
                      >
                        {t('search.clearAll')}
                      </button>
                    )}
                    <button
                      onClick={() => setHistoryOpen(false)}
                      className="p-1 rounded hover:bg-[var(--bg-tertiary)] transition-colors"
                    >
                      <X className="h-4 w-4 text-[var(--text-tertiary)]" />
                    </button>
                  </div>
                </div>
                {historyItems.length > 0 ? (
                  <div className="space-y-1">
                    {historyItems.slice(0, 20).map((item: HistoryItem) => (
                      <div
                        key={item.id}
                        className="group flex items-center gap-2 p-2.5 rounded-lg hover:bg-[var(--bg-primary)] cursor-pointer transition-colors"
                        onClick={() => handleHistoryClick(item)}
                      >
                        <History className="h-3.5 w-3.5 text-[var(--text-tertiary)] flex-shrink-0" />
                        <span className="flex-1 text-sm text-[var(--text-secondary)] truncate">{item.query}</span>
                        <button
                          onClick={(e) => { e.stopPropagation(); deleteHistoryMutation.mutate(item.id) }}
                          className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
                        >
                          <Trash2 className="h-3.5 w-3.5 text-red-400" />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-[var(--text-tertiary)] text-center py-8">{t('search.noResults')}</p>
                )}
              </div>
            </div>
          )}

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Search Hero Bar */}
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-3">
                <form onSubmit={handleSearch} className="flex-1 relative">
                  {/* Both icons embedded inside the input, text starts after them */}
                  {user && !historyOpen && (
                    <button
                      type="button"
                      onClick={() => setHistoryOpen(true)}
                      className="absolute start-3 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-[var(--bg-tertiary)] flex items-center justify-center hover:bg-[var(--border-default)] transition-colors z-20"
                    >
                      <History className="h-4 w-4 text-[var(--text-secondary)]" />
                    </button>
                  )}
                  <SearchIcon className={`absolute top-1/2 -translate-y-1/2 h-5 w-5 text-primary-500 pointer-events-none z-20 ${user && !historyOpen ? 'start-[52px]' : 'start-6'}`} />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => handleQueryChange(e.target.value)}
                    placeholder={t('search.placeholder')}
                    className={`relative w-full py-4 rounded-2xl border-2 border-[var(--border-default)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-primary-500 dark:focus:border-primary-400 transition-all text-base shadow-sm focus:shadow-md focus:ring-4 focus:ring-primary-500/10 z-10`}
                    style={{
                      paddingLeft: user && !historyOpen ? '4.5rem' : '3rem',
                      paddingRight: '8rem',
                    }}
                    autoFocus
                  />
                  <button
                    type="submit"
                    className="absolute end-2 top-1/2 -translate-y-1/2 bg-primary-500 text-white px-5 py-2 rounded-xl hover:bg-primary-600 flex items-center gap-2 text-sm font-medium transition-colors shadow-sm shadow-primary-500/20"
                  >
                    <SearchIcon className="h-4 w-4" />
                    <span className="hidden sm:inline">{t('search.btn')}</span>
                  </button>
                </form>
              </div>

              {/* Filter bar */}
              <div className="flex items-center gap-3 flex-wrap">
                <button
                  onClick={() => setFiltersOpen(!filtersOpen)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    filtersOpen || hasFilters
                      ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800 text-primary-700 dark:text-primary-300'
                      : 'bg-[var(--bg-primary)] border-[var(--border-default)] text-[var(--text-secondary)] hover:border-[var(--text-tertiary)]'
                  }`}
                >
                  <SlidersHorizontal className="h-3.5 w-3.5" />
                  {t('search.filters')}
                  {hasFilters && (
                    <span className="w-4 h-4 rounded-full bg-primary-500 text-white text-[10px] flex items-center justify-center">
                      {[court, dateMin, dateMax, caseType, courtLevel, minCitations, hasText].filter(Boolean).length}
                    </span>
                  )}
                </button>

                {hasFilters && (
                  <button
                    onClick={clearFilters}
                    className="text-xs text-[var(--text-tertiary)] hover:text-red-500 transition-colors underline-offset-2 hover:underline"
                  >
                    {t('search.clearFilters')}
                  </button>
                )}

                <div className="hidden sm:flex items-center gap-2 ml-auto">
                  <span className="text-xs text-[var(--text-tertiary)]">{t('search.tryThese')}</span>
                  {[t('search.sample.contractBreach'), t('search.sample.negligence'), t('search.sample.patent')].map((term) => (
                    <button
                      key={term}
                      onClick={() => handleQueryChange(term)}
                      className="px-2.5 py-1 rounded-full text-xs bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--border-default)] hover:text-[var(--text-primary)] transition-colors border border-transparent hover:border-[var(--border-default)]"
                    >
                      {term}
                    </button>
                  ))}
                </div>
              </div>

              {/* Expanded filters */}
              {filtersOpen && (
                <div className="mt-3 p-4 bg-[var(--bg-primary)] rounded-2xl border border-[var(--border-default)] shadow-sm grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 animate-slide-down">
                  {/* Court */}
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">{t('search.court')}</label>
                    <select
                      value={court}
                      onChange={(e) => { setCourt(e.target.value); setPage(1); }}
                      className="w-full px-3 py-2 rounded-xl text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                    >
                      <option value="">{t('search.court')}</option>
                      {['ca9', 'ca2', 'ca5', 'ca1', 'ca3', 'ca4', 'ca6', 'ca7', 'ca8', 'ca10', 'ca11', 'cadc', 'cafc'].map((c) => (
                        <option key={c} value={c}>{c.toUpperCase()}</option>
                      ))}
                    </select>
                  </div>

                  {/* Case Type */}
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">{t('search.caseType')}</label>
                    <select
                      value={caseType}
                      onChange={(e) => { setCaseType(e.target.value); setPage(1); }}
                      className="w-full px-3 py-2 rounded-xl text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                    >
                      <option value="">{t('search.caseType')}</option>
                      <option value="civil">{t('search.caseTypeCivil')}</option>
                      <option value="criminal">{t('search.caseTypeCriminal')}</option>
                      <option value="administrative">{t('search.caseTypeAdmin')}</option>
                      <option value="bankruptcy">{t('search.caseTypeOther')}</option>
                      <option value="patent">Patent</option>
                      <option value="trademark">Trademark</option>
                      <option value="other">{t('search.caseTypeOther')}</option>
                    </select>
                  </div>

                  {/* Court Level */}
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">{t('search.courtLevel')}</label>
                    <select
                      value={courtLevel}
                      onChange={(e) => { setCourtLevel(e.target.value); setPage(1); }}
                      className="w-full px-3 py-2 rounded-xl text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                    >
                      <option value="">{t('search.all')}</option>
                      <option value="supreme">{t('search.supreme')}</option>
                      <option value="circuit">{t('search.circuit')}</option>
                      <option value="district">{t('search.district')}</option>
                      <option value="state">{t('search.state')}</option>
                    </select>
                  </div>

                  {/* Date from */}
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">{t('search.dateFrom')}</label>
                    <input
                      type="date"
                      value={dateMin}
                      onChange={(e) => { setDateMin(e.target.value); setPage(1); }}
                      className="w-full px-3 py-2 rounded-xl text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                    />
                  </div>

                  {/* Date to */}
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">{t('search.dateTo')}</label>
                    <input
                      type="date"
                      value={dateMax}
                      onChange={(e) => { setDateMax(e.target.value); setPage(1); }}
                      className="w-full px-3 py-2 rounded-xl text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                    />
                  </div>

                  {/* Min Citations */}
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">{t('search.minCitations')}</label>
                    <input
                      type="number"
                      min="0"
                      placeholder="e.g. 5"
                      value={minCitations}
                      onChange={(e) => { setMinCitations(e.target.value); setPage(1); }}
                      className="w-full px-3 py-2 rounded-xl text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                    />
                  </div>

                  {/* Has Full Text */}
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">{t('search.hasFullText')}</label>
                    <select
                      value={hasText}
                      onChange={(e) => { setHasText(e.target.value); setPage(1); }}
                      className="w-full px-3 py-2 rounded-xl text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                    >
                      <option value="">{t('search.all')}</option>
                      <option value="true">{t('search.hasFullTextYes')}</option>
                      <option value="false">{t('search.hasFullTextNo')}</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            {/* Results */}
            <div className="space-y-4">
              {/* Results count */}
              {results.length > 0 && (
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="px-3 py-1.5 rounded-full bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800/40">
                      <span className="text-sm font-semibold text-primary-700 dark:text-primary-300">
                        {totalResults.toLocaleString()} {t('search.cases')}
                      </span>
                    </div>
                    {query && (
                      <span className="text-sm text-[var(--text-secondary)]">
                        {t('search.for')} "<span className="font-medium text-[var(--text-primary)]">{query}</span>"
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-[var(--text-tertiary)] hidden sm:block">
                    {t('search.showing').replace('{from}', String(from)).replace('{to}', String(to)).replace('{total}', totalResults.toLocaleString())}
                  </span>
                </div>
              )}

              {/* Loading */}
              {isLoading && (
                <div className="flex flex-col items-center justify-center py-20">
                  <div className="relative">
                    <div className="w-16 h-16 rounded-full border-4 border-primary-100 dark:border-primary-900/30 animate-pulse" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Loader2 className="h-7 w-7 animate-spin text-primary-500" />
                    </div>
                  </div>
                  <p className="mt-4 text-sm text-[var(--text-secondary)]">{t('search.searching')}</p>
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="p-6 rounded-2xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/40">
                  <p className="text-sm font-medium text-red-800 dark:text-red-200">{t('common.error')}</p>
                  <button onClick={() => window.location.reload()} className="text-xs text-red-600 dark:text-red-400 underline mt-1">
                    {t('common.retry')}
                  </button>
                </div>
              )}

              {/* Empty - no query */}
              {!isLoading && query.length <= 2 && (
                <div className="text-center py-16">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-[var(--bg-tertiary)] mb-6">
                    <SearchIcon className="h-10 w-10 text-[var(--text-tertiary)]" />
                  </div>
                  <h3 className="text-xl font-serif font-bold text-[var(--text-primary)] mb-2">{t('search.title')}</h3>
                  <p className="text-[var(--text-secondary)] text-sm max-w-md mx-auto mb-8">{t('search.enterChars')}</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {[
                      { label: t('search.sample.contractBreach'), key: 'contractBreach' },
                      { label: t('search.sample.negligence'), key: 'negligence' },
                      { label: t('search.sample.patent'), key: 'patent' },
                      { label: t('search.sample.trademark'), key: 'trademark' },
                      { label: t('search.sample.employment'), key: 'employment' },
                    ].map((item) => (
                      <button
                        key={item.key}
                        onClick={() => handleQueryChange(item.label)}
                        className="group px-4 py-2 rounded-xl text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] text-[var(--text-secondary)] hover:border-primary-300 dark:hover:border-primary-600 hover:text-primary-700 dark:hover:text-primary-300 hover:shadow-sm transition-all flex items-center gap-2"
                      >
                        <span>{item.label}</span>
                        <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                  </div>
                  <div className="mt-10 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40">
                    <Sparkles className="h-3.5 w-3.5 text-amber-500" />
                    <span className="text-xs text-amber-700 dark:text-amber-300">{t('search.aiPowered')}</span>
                  </div>
                </div>
              )}

              {/* No results */}
              {!isLoading && query.length > 2 && results.length === 0 && (
                <div className="bg-[var(--bg-primary)] rounded-2xl p-12 text-center border border-[var(--border-default)] shadow-sm">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[var(--bg-tertiary)] mb-4">
                    <FileText className="h-8 w-8 text-[var(--text-tertiary)]" />
                  </div>
                  <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{t('search.noResults')}</h3>
                  <p className="text-sm text-[var(--text-secondary)] mb-4">{t('search.tip')}</p>
                  <button
                    onClick={() => { setQuery(''); setPage(1); }}
                    className="text-sm text-primary-500 font-medium hover:underline"
                  >
                    {t('search.clearSearch')}
                  </button>
                </div>
              )}

              {/* Result cards */}
              {results.map((result: CaseResult) => (
                <div
                  key={result.id}
                  className="stagger-item group bg-[var(--bg-primary)] rounded-2xl p-5 border border-[var(--border-default)] hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-lg cursor-pointer transition-all duration-200"
                  onClick={() => navigate(result.slug_url || `/cases/${result.id}`)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-[var(--bg-tertiary)] text-[var(--text-secondary)] border border-[var(--border-default)]">
                          {result.court || t('search.federalCourt')}
                        </span>
                        {result.citation && (
                          <span className="text-[11px] text-[var(--text-tertiary)] font-mono">{result.citation}</span>
                        )}
                        {result.has_text === true && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800/40">
                            <FileText className="h-3 w-3" />
                            {t('search.hasFullTextYes')}
                          </span>
                        )}
                        {result.has_text === false && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800/40">
                            <File className="h-3 w-3" />
                            {t('search.hasFullTextNo')}
                          </span>
                        )}
                      </div>
                      <h3 className="text-base font-semibold text-[var(--text-primary)] group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2 leading-snug">
                        {result.case_name}
                      </h3>
                      <div className="flex items-center gap-4 mt-3 text-sm text-[var(--text-secondary)]">
                        {result.date_filed && (
                          <div className="flex items-center gap-1.5">
                            <Calendar className="h-3.5 w-3.5" />
                            <span>{new Date(result.date_filed).toLocaleDateString(language === 'zh' ? 'zh-CN' : 'en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
                          </div>
                        )}
                        {result.docket_number && (
                          <div className="hidden sm:flex items-center gap-1.5">
                            <FileText className="h-3.5 w-3.5" />
                            <span className="font-mono text-xs">{result.docket_number}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0 flex items-center gap-2">
                      <button
                        onClick={(e) => { e.stopPropagation(); navigate(result.slug_url || `/cases/${result.id}`); }}
                        className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-primary-50 dark:hover:bg-primary-900/20 hover:text-primary-700 dark:hover:text-primary-300 border border-[var(--border-default)] hover:border-primary-200 dark:hover:border-primary-700 transition-all opacity-0 group-hover:opacity-100"
                      >
                        {t('case.viewDetails')}
                        <ArrowRight className="h-3 w-3" />
                      </button>
                      <div className="sm:hidden w-8 h-8 rounded-xl bg-[var(--bg-secondary)] flex items-center justify-center text-[var(--text-tertiary)]">
                        <ChevronRightIcon className="h-4 w-4" />
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Pagination */}
              {results.length > 0 && totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-8">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage <= 1}
                    className="flex items-center gap-1 px-3 py-2 rounded-xl text-sm border bg-[var(--bg-primary)] border-[var(--border-default)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft className="h-4 w-4" />
                    <span className="hidden sm:inline">{t('search.prevPage')}</span>
                  </button>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum: number
                      if (totalPages <= 5) pageNum = i + 1
                      else if (currentPage <= 3) pageNum = i + 1
                      else if (currentPage >= totalPages - 2) pageNum = totalPages - 4 + i
                      else pageNum = currentPage - 2 + i
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setPage(pageNum)}
                          className={`w-9 h-9 rounded-xl text-sm font-medium transition-colors ${
                            pageNum === currentPage
                              ? 'bg-primary-500 text-white shadow-sm shadow-primary-500/30'
                              : 'bg-[var(--bg-primary)] border border-[var(--border-default)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}
                  </div>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage >= totalPages}
                    className="flex items-center gap-1 px-3 py-2 rounded-xl text-sm border bg-[var(--bg-primary)] border-[var(--border-default)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    <span className="hidden sm:inline">{t('search.nextPage')}</span>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              )}
              {results.length > 0 && totalPages > 1 && (
                <p className="text-center text-xs text-[var(--text-tertiary)] mt-3">
                  {t('search.page').replace('{current}', String(currentPage)).replace('{total}', String(totalPages))}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
