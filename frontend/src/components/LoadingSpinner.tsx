import React from 'react';

type SpinnerSize = 'sm' | 'md' | 'lg' | 'xl';
type SpinnerVariant = 'primary' | 'white' | 'gray';

interface LoadingSpinnerProps {
  size?: SpinnerSize;
  variant?: SpinnerVariant;
  label?: string;
  fullPage?: boolean;
  className?: string;
}

const sizeStyles: Record<SpinnerSize, string> = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
  xl: 'h-16 w-16 border-4',
};

const variantStyles: Record<SpinnerVariant, string> = {
  primary: 'border-primary-200 border-t-primary-500',
  white: 'border-white/30 border-t-white',
  gray: 'border-gray-200 border-t-gray-500',
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'primary',
  label = 'Loading...',
  fullPage = false,
  className = '',
}) => {
  const spinner = (
    <div
      className={`inline-flex flex-col items-center gap-3 ${className}`}
      role="status"
      aria-live="polite"
    >
      <span
        className={[
          'rounded-full animate-spin',
          sizeStyles[size],
          variantStyles[variant],
        ]
          .join(' ')
          .trim()}
        aria-hidden="true"
      />
      {label && (
        <span className="text-sm font-medium text-gray-500">{label}</span>
      )}
    </div>
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-50">
        <div className="flex flex-col items-center gap-4">
          {spinner}
        </div>
      </div>
    );
  }

  return spinner;
};

export default LoadingSpinner;
