import { AlertCircle, Wifi, Clock, XCircle, AlertTriangle, RefreshCw } from 'lucide-react'

type ErrorType = 'not_found' | 'rate_limit' | 'server_error' | 'network' | 'unknown'

interface ErrorStateProps {
  type?: ErrorType
  title?: string
  description?: string
  onRetry?: () => void
  className?: string
}

const errorConfig: Record<ErrorType, { icon: typeof AlertCircle; iconBg: string; iconColor: string }> = {
  not_found: { icon: XCircle, iconBg: 'bg-gray-100 dark:bg-gray-800', iconColor: 'text-gray-500' },
  rate_limit: { icon: Clock, iconBg: 'bg-amber-100 dark:bg-amber-900/30', iconColor: 'text-amber-500' },
  server_error: { icon: Wifi, iconBg: 'bg-red-100 dark:bg-red-900/30', iconColor: 'text-red-500' },
  network: { icon: AlertTriangle, iconBg: 'bg-orange-100 dark:bg-orange-900/30', iconColor: 'text-orange-500' },
  unknown: { icon: AlertCircle, iconBg: 'bg-gray-100 dark:bg-gray-800', iconColor: 'text-gray-500' },
}

const defaultMessages: Record<ErrorType, { title: string; description: string }> = {
  not_found: {
    title: 'Not Found',
    description: 'The resource you\'re looking for doesn\'t exist or has been removed.',
  },
  rate_limit: {
    title: 'Too Many Requests',
    description: 'You\'re making requests too quickly. Please wait a moment and try again.',
  },
  server_error: {
    title: 'Service Unavailable',
    description: 'The service is temporarily unavailable. Please try again in a few minutes.',
  },
  network: {
    title: 'Network Error',
    description: 'Unable to connect to the server. Please check your internet connection.',
  },
  unknown: {
    title: 'Something Went Wrong',
    description: 'An unexpected error occurred. Please try again.',
  },
}

export function ErrorState({
  type = 'unknown',
  title,
  description,
  onRetry,
  className = '',
}: ErrorStateProps) {
  const config = errorConfig[type]
  const messages = defaultMessages[type]
  const Icon = config.icon

  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 text-center ${className}`}>
      <div className={`w-14 h-14 rounded-2xl ${config.iconBg} flex items-center justify-center mb-5`}>
        <Icon className={`h-7 w-7 ${config.iconColor}`} />
      </div>
      <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">
        {title || messages.title}
      </h3>
      <p className="text-sm text-[var(--text-secondary)] max-w-sm mb-6">
        {description || messages.description}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors text-sm font-medium shadow-sm"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
      )}
    </div>
  )
}

export default ErrorState
