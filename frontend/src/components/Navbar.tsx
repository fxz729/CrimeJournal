import React, { useState, useRef, useEffect } from 'react';

export interface NavLink {
  label: string;
  href: string;
  active?: boolean;
}

interface NavbarProps {
  logo?: string;
  logoText?: string;
  links?: NavLink[];
  userMenu?: {
    name: string;
    email?: string;
    avatar?: string;
    menuItems?: { label: string; onClick: () => void; variant?: 'default' | 'destructive' }[];
  };
  onLinkClick?: (href: string) => void;
  className?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  logo,
  logoText = 'CrimeJournal',
  links = [],
  userMenu,
  onLinkClick,
  className = '',
}) => {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <nav
      className={`bg-white border-b border-gray-200 sticky top-0 z-50 ${className}`}
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            {logo ? (
              <img src={logo} alt={`${logoText} logo`} className="h-8 w-auto object-contain" />
            ) : (
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                </div>
                <span className="font-serif font-bold text-xl text-gray-900">
                  {logoText}
                </span>
              </div>
            )}
          </div>

          {/* Desktop Navigation Links */}
          {links.length > 0 && (
            <div className="hidden md:flex items-center gap-1">
              {links.map((link) => (
                <button
                  key={link.href}
                  onClick={() => onLinkClick?.(link.href)}
                  className={[
                    'px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                    link.active
                      ? 'text-primary-600 bg-primary-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
                  ].join(' ')}
                  aria-current={link.active ? 'page' : undefined}
                >
                  {link.label}
                </button>
              ))}
            </div>
          )}

          {/* Right Side */}
          <div className="flex items-center gap-3">
            {/* User Menu */}
            {userMenu && (
              <div ref={userMenuRef} className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center gap-2 p-1 rounded-full hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
                  aria-haspopup="true"
                  aria-expanded={isUserMenuOpen}
                >
                  {userMenu.avatar ? (
                    <img
                      src={userMenu.avatar}
                      alt={userMenu.name}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                      <span className="text-sm font-semibold text-primary-600">
                        {userMenu.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  )}
                  <span className="hidden sm:block text-sm font-medium text-gray-700">
                    {userMenu.name}
                  </span>
                  <svg
                    className={`hidden sm:block w-4 h-4 text-gray-400 transition-transform ${isUserMenuOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden z-50">
                    <div className="px-4 py-3 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {userMenu.name}
                      </p>
                      {userMenu.email && (
                        <p className="text-xs text-gray-500 truncate mt-0.5">
                          {userMenu.email}
                        </p>
                      )}
                    </div>
                    <div className="py-1">
                      {userMenu.menuItems?.map((item, index) => (
                        <button
                          key={index}
                          onClick={() => {
                            item.onClick();
                            setIsUserMenuOpen(false);
                          }}
                          className={[
                            'w-full text-left px-4 py-2 text-sm transition-colors',
                            item.variant === 'destructive'
                              ? 'text-red-600 hover:bg-red-50'
                              : 'text-gray-700 hover:bg-gray-50',
                          ].join(' ')}
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Mobile Menu Button */}
            {links.length > 0 && (
              <button
                className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                aria-label="Toggle mobile menu"
                aria-expanded={isMobileMenuOpen}
              >
                {isMobileMenuOpen ? (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && links.length > 0 && (
          <div className="md:hidden py-3 border-t border-gray-100">
            {links.map((link) => (
              <button
                key={link.href}
                onClick={() => {
                  onLinkClick?.(link.href);
                  setIsMobileMenuOpen(false);
                }}
                className={[
                  'w-full text-left px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                  link.active
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50',
                ].join(' ')}
                aria-current={link.active ? 'page' : undefined}
              >
                {link.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
