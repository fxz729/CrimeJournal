interface SkeletonProps {
  variant?: 'line' | 'card' | 'circle' | 'rect'
  width?: string | number
  height?: string | number
  className?: string
  lines?: number
}

export function Skeleton({ variant = 'line', width, height, className = '', lines = 3 }: SkeletonProps) {
  const baseClass = 'skeleton-line rounded animate-skeleton-shimmer'

  if (variant === 'card') {
    return (
      <div className={`bg-[var(--bg-primary)] rounded-xl border border-[var(--border-default)] p-6 space-y-4 ${className}`}>
        <Skeleton variant="line" width="60%" height="1.5rem" />
        <div className="flex gap-4">
          <Skeleton variant="line" width="30%" height="1rem" />
          <Skeleton variant="line" width="25%" height="1rem" />
        </div>
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton key={i} variant="line" height="0.875rem" className={i === lines - 1 ? 'w-4/5' : 'w-full'} />
        ))}
      </div>
    )
  }

  if (variant === 'circle') {
    return (
      <div
        className={`rounded-full animate-skeleton-shimmer bg-[var(--bg-tertiary)] ${className}`}
        style={{ width: width || '2.5rem', height: height || '2.5rem' }}
      />
    )
  }

  return (
    <div
      className={`${baseClass} ${className}`}
      style={{
        width: width || '100%',
        height: height || '1rem',
      }}
    />
  )
}

export function SkeletonText({ lines = 3, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          height="0.875rem"
          className={i === lines - 1 ? 'w-3/4' : 'w-full'}
        />
      ))}
    </div>
  )
}

export default Skeleton
