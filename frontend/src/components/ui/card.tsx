import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  hoverable?: boolean  // alias for hover
  padding?: 'none' | 'sm' | 'md' | 'lg'
  accentColor?: 'primary' | 'emerald' | 'amber' | 'red' | 'none'
  onClick?: () => void
}

const paddingStyles = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

export function Card({
  children,
  className = '',
  hover = false,
  hoverable = false,
  padding = 'md',
  accentColor = 'none',
  onClick,
}: CardProps) {
  const isHoverable = hover || hoverable
  const accentColors = {
    primary: 'border-l-4 border-l-primary-500',
    emerald: 'border-l-4 border-l-emerald-500',
    amber: 'border-l-4 border-l-amber-500',
    red: 'border-l-4 border-l-red-500',
    none: '',
  }

  return (
    <div
      onClick={onClick}
      className={`
        bg-[var(--bg-primary)] rounded-xl border border-[var(--border-default)]
        shadow-sm ${paddingStyles[padding]} ${accentColors[accentColor]}
        ${isHoverable ? 'hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 cursor-pointer' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  )
}

export default Card
