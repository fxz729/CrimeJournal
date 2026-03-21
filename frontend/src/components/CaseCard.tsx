import React from 'react';
import { Card } from './ui/card';

export interface CaseData {
  id: string;
  caseName: string;
  court: string;
  date: string;
  citation?: string;
  tags?: string[];
  summary?: string;
}

interface CaseCardProps {
  caseData: CaseData;
  onClick?: (id: string) => void;
  className?: string;
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
};

export const CaseCard: React.FC<CaseCardProps> = ({
  caseData,
  onClick,
  className = '',
}) => {
  const handleClick = () => {
    onClick?.(caseData.id);
  };

  return (
    <Card hoverable onClick={handleClick} className={`group ${className}`}>
      <div className="flex flex-col gap-3">
        {/* Case Name */}
        <h3 className="font-serif text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors duration-200 line-clamp-2">
          {caseData.caseName}
        </h3>

        {/* Metadata Row */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500">
          {/* Court */}
          <div className="flex items-center gap-1.5">
            <svg
              className="w-4 h-4 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v5m-4 0h4"
              />
            </svg>
            <span className="truncate max-w-[150px]" title={caseData.court}>
              {caseData.court}
            </span>
          </div>

          {/* Date */}
          <div className="flex items-center gap-1.5">
            <svg
              className="w-4 h-4 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2z"
              />
            </svg>
            <time dateTime={caseData.date}>{formatDate(caseData.date)}</time>
          </div>

          {/* Citation */}
          {caseData.citation && (
            <div className="flex items-center gap-1.5">
              <svg
                className="w-4 h-4 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"
                />
              </svg>
              <span className="truncate max-w-[200px] italic" title={caseData.citation}>
                {caseData.citation}
              </span>
            </div>
          )}
        </div>

        {/* Summary */}
        {caseData.summary && (
          <p className="text-sm text-gray-600 line-clamp-3">{caseData.summary}</p>
        )}

        {/* Tags */}
        {caseData.tags && caseData.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-1">
            {caseData.tags.slice(0, 5).map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded-full"
              >
                {tag}
              </span>
            ))}
            {caseData.tags.length > 5 && (
              <span className="px-2 py-0.5 text-xs text-gray-400">
                +{caseData.tags.length - 5} more
              </span>
            )}
          </div>
        )}

        {/* Hover Indicator */}
        <div className="flex items-center gap-1 text-primary-500 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <span>View Details</span>
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </div>
    </Card>
  );
};

export default CaseCard;
