import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search as SearchIcon, Filter, Loader2, FileText, Calendar, MapPin } from 'lucide-react'
import { casesApi } from '../lib/api'
import { useI18n } from '../lib/i18n'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { useAuth } from '../lib/auth'

interface CaseResult {
  id: number
  courtlistener_id: number
  case_name: string
  court: string
  date_filed: string
  citation: string
  docket_number: string
}

export default function Search() {
  const [query, setQuery] = useState('')
  const [court, setCourt] = useState('')
  const [dateMin, setDateMin] = useState('')
  const [dateMax, setDateMax] = useState('')
  const navigate = useNavigate()
  const { t } = useI18n()
  const { user } = useAuth()

  const filters: Record<string, string> = {}
  if (court) filters.court = court
  if (dateMin) filters.date_min = dateMin
  if (dateMax) filters.date_max = dateMax

  const { data, isLoading, error } = useQuery({
    queryKey: ['search', query, court, dateMin, dateMax],
    queryFn: () => casesApi.search(query, 1, filters),
    enabled: query.length > 2,
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
  }

  const clearFilters = () => {
    setCourt('')
    setDateMin('')
    setDateMax('')
  }

  const hasFilters = court || dateMin || dateMax

  const results = data?.data?.results || []

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-6 w-6 text-primary-600" />
            <span className="font-serif text-xl font-bold">CrimeJournal</span>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <button
              onClick={() => navigate(user ? '/favorites' : '/login')}
              className="text-gray-600 hover:text-gray-900"
            >
              {t('nav.favorites')}
            </button>
            <button
              onClick={() => navigate(user ? '/account' : '/login')}
              className="text-gray-600 hover:text-gray-900"
            >
              {t('nav.account')}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Form */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t('search.placeholder')}
                className="w-full pl-12 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
              />
            </div>
            <button
              type="submit"
              className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 flex items-center gap-2"
            >
              <SearchIcon className="h-5 w-5" />
              {t('search.btn')}
            </button>
          </form>

          {/* Filters */}
          <div className="mt-4 flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Filter className="h-4 w-4" />
              <span>{t('search.filters')}</span>
            </div>
            <select
              value={court}
              onChange={(e) => setCourt(e.target.value)}
              className="px-3 py-1 border rounded-md text-sm"
            >
              <option value="">{t('search.court')}</option>
              <option value="ca9">9th Circuit</option>
              <option value="ca2">2nd Circuit</option>
              <option value="ca5">5th Circuit</option>
              <option value="ca1">1st Circuit</option>
              <option value="ca3">3rd Circuit</option>
              <option value="ca4">4th Circuit</option>
              <option value="ca6">6th Circuit</option>
              <option value="ca7">7th Circuit</option>
              <option value="ca8">8th Circuit</option>
              <option value="ca10">10th Circuit</option>
              <option value="ca11">11th Circuit</option>
              <option value="cadc">DC Circuit</option>
              <option value="cafc">Federal Circuit</option>
            </select>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-500">{t('search.dateFrom')}:</span>
              <input
                type="date"
                value={dateMin}
                onChange={(e) => setDateMin(e.target.value)}
                className="px-3 py-1 border rounded-md text-sm"
              />
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-500">{t('search.dateTo')}:</span>
              <input
                type="date"
                value={dateMax}
                onChange={(e) => setDateMax(e.target.value)}
                className="px-3 py-1 border rounded-md text-sm"
              />
            </div>
            {hasFilters && (
              <button
                onClick={clearFilters}
                className="text-sm text-primary-600 hover:underline"
              >
                {t('search.clearFilters')}
              </button>
            )}
          </div>
        </div>

        {/* Results */}
        <div className="space-y-4">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            </div>
          )}

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
              <span>{t('common.error')}</span>
              <button
                onClick={() => window.location.reload()}
                className="ml-auto text-sm underline hover:no-underline"
              >
                {t('common.retry')}
              </button>
            </div>
          )}

          {!isLoading && query.length > 2 && results.length === 0 && (
            <div className="bg-white rounded-xl p-12 text-center">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">{t('search.noResults')}</h3>
              <p className="text-gray-600">{t('search.tip')}</p>
            </div>
          )}

          {results.map((result: CaseResult) => (
            <div
              key={result.id}
              className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition cursor-pointer"
              onClick={() => navigate(`/cases/${result.courtlistener_id}`)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-primary-600 hover:underline mb-2">
                    {result.case_name}
                  </h3>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {result.court || t('common.noData')}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {result.date_filed ? new Date(result.date_filed).toLocaleDateString() : t('common.noData')}
                    </div>
                    {result.citation && (
                      <div className="flex items-center gap-1">
                        <FileText className="h-4 w-4" />
                        {result.citation}
                      </div>
                    )}
                  </div>
                </div>
                <button className="text-gray-400 hover:text-primary-600">
                  {t('case.viewDetails')} &rarr;
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Tips when no query */}
        {query.length <= 2 && (
          <div className="bg-white rounded-xl p-12 text-center">
            <h3 className="text-lg font-semibold mb-4">{t('search.title')}</h3>
            <p className="text-gray-600 mb-4">
              {t('search.enterChars')}
            </p>
            <div className="text-sm text-gray-500">
              <p>{t('search.trySearching')}</p>
              <div className="flex gap-2 justify-center mt-2 flex-wrap">
                {['contract breach', 'negligence', 'patent', 'trademark', 'employment'].map((term) => (
                  <button
                    key={term}
                    onClick={() => setQuery(term)}
                    className="px-3 py-1 bg-gray-100 rounded-full hover:bg-gray-200"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
