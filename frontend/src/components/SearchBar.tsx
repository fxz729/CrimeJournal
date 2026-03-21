import React, { useState, useRef, useEffect } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';

export interface FilterOption {
  value: string;
  label: string;
}

interface SearchBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  onFilterChange?: (filter: string) => void;
  filters?: FilterOption[];
  defaultFilter?: string;
  isLoading?: boolean;
  className?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Search cases...',
  onSearch,
  onFilterChange,
  filters = [],
  defaultFilter = '',
  isLoading = false,
  className = '',
}) => {
  const [query, setQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState(defaultFilter);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (filterRef.current && !filterRef.current.contains(event.target as Node)) {
        setIsFilterOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    onSearch('');
  };

  const handleFilterSelect = (value: string) => {
    setSelectedFilter(value);
    setIsFilterOpen(false);
    onFilterChange?.(value);
  };

  const selectedLabel =
    filters.find((f) => f.value === selectedFilter)?.label ?? 'All';

  return (
    <form onSubmit={handleSearch} className={`flex flex-col gap-3 ${className}`}>
      <div className="flex gap-2 flex-col sm:flex-row">
        <div className="relative flex-1">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            leftIcon={
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
                  d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"
                />
              </svg>
            }
            rightIcon={
              query ? (
                <button
                  type="button"
                  onClick={handleClear}
                  className="hover:text-gray-600 transition-colors"
                  aria-label="Clear search"
                >
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              ) : undefined
            }
            fullWidth
            aria-label="Search input"
          />
        </div>

        {filters.length > 0 && (
          <div ref={filterRef} className="relative min-w-[140px]">
            <button
              type="button"
              onClick={() => setIsFilterOpen(!isFilterOpen)}
              className={[
                'w-full px-4 py-2.5 text-base bg-white border rounded-lg',
                'flex items-center justify-between gap-2',
                'hover:border-gray-400 transition-colors duration-200',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                isFilterOpen ? 'border-primary-500 ring-2 ring-primary-500' : 'border-gray-300',
              ].join(' ')}
              aria-haspopup="listbox"
              aria-expanded={isFilterOpen}
            >
              <span className="text-gray-700 truncate">{selectedLabel}</span>
              <svg
                className={`w-4 h-4 flex-shrink-0 transition-transform ${isFilterOpen ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {isFilterOpen && (
              <ul
                className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden"
                role="listbox"
              >
                {filters.map((filter) => (
                  <li
                    key={filter.value}
                    onClick={() => handleFilterSelect(filter.value)}
                    role="option"
                    aria-selected={selectedFilter === filter.value}
                    className={[
                      'px-4 py-2 cursor-pointer transition-colors',
                      selectedFilter === filter.value
                        ? 'bg-primary-50 text-primary-600 font-medium'
                        : 'hover:bg-gray-50 text-gray-700',
                    ].join(' ')}
                  >
                    {filter.label}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        <Button
          type="submit"
          isLoading={isLoading}
          aria-label="Search"
        >
          Search
        </Button>
      </div>
    </form>
  );
};

export default SearchBar;
