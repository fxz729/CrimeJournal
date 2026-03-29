import { ReactNode } from 'react'
import { Inbox, Search, FileText, Star, Bookmark } from 'lucide-react'

type EmptyVariant = 'generic' | 'search' | 'cases' | 'favorites' | 'bookmarks'

interface EmptyStateProps {
  variant?: EmptyVariant
  title?: string
  description?: string
  action?: ReactNode
  className?: string
}

const variantConfig: Record<EmptyVariant, { icon: typeof Inbox; iconBg: string; defaultTitle: string; defaultDesc: string }> = {
  generic: {
    icon: Inbox,
    iconBg: 'bg-gray-100 dark:bg-gray-800',
    defaultTitle: 'Nothing here yet',
    defaultDesc: 'There\'s nothing to show at the moment.',
  },
  search: {
    icon: Search,
    iconBg: 'bg-primary-50 dark:bg-primary-900/20',
    defaultTitle: 'No results found',
    defaultDesc: 'Try adjusting your search or filters to find what you\'re looking for.',
  },
  cases: {
    icon: FileText,
    iconBg: 'bg-blue-50 dark:bg-blue-900/20',
    defaultTitle: 'No cases yet',
    defaultDesc: 'Start by searching for legal cases to build your collection.',
  },
  favorites: {
    icon: Star,
    iconBg: 'bg-yellow-50 dark:bg-yellow-900/20',
    defaultTitle: 'No favorites yet',
    defaultDesc: 'Save cases you find interesting for quick access later.',
  },
  bookmarks: {
    icon: Bookmark,
    iconBg: 'bg-violet-50 dark:bg-violet-900/20',
    defaultTitle: 'No bookmarks',
    defaultDesc: 'Bookmark items to save them for later.',
  },
}

export function EmptyState({
  variant = 'generic',
  title,
  description,
  action,
  className = '',
}: EmptyStateProps) {
  const config = variantConfig[variant]
  const Icon = config.icon

  return (
    <div className={`flex flex-col items-center justify-center py-16 px-4 text-center ${className}`}>
      <div className={`w-16 h-16 rounded-2xl ${config.iconBg} flex items-center justify-center mb-6`}>
        <Icon className="h-8 w-8 text-[var(--text-tertiary)]" />
      </div>
      <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">
        {title || config.defaultTitle}
      </h3>
      <p className="text-sm text-[var(--text-secondary)] max-w-sm mb-6">
        {description || config.defaultDesc}
      </p>
      {action && <div>{action}</div>}
    </div>
  )
}

export default EmptyState
