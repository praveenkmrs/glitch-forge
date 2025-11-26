/**
 * Navigation Header Component
 *
 * Displays app navigation with user menu and logout functionality.
 */

import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

export const Navigation = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const isActive = (path: string) => location.pathname === path

  const navLinkClass = (path: string) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive(path)
        ? 'bg-blue-700 text-white'
        : 'text-blue-100 hover:bg-blue-600 hover:text-white'
    }`

  return (
    <nav className="bg-blue-500 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and desktop nav */}
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/dashboard" className="text-white text-xl font-bold">
                HITL Service
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-4 items-center">
              <Link to="/dashboard" className={navLinkClass('/dashboard')}>
                Dashboard
              </Link>
              <Link to="/admin" className={navLinkClass('/admin')}>
                API Keys
              </Link>
            </div>
          </div>

          {/* User menu (desktop) */}
          <div className="hidden sm:ml-6 sm:flex sm:items-center">
            <div className="flex items-center space-x-4">
              <div className="text-blue-100 text-sm">
                <div className="font-medium">{user?.name || 'User'}</div>
                <div className="text-xs text-blue-200">{user?.email}</div>
              </div>
              <button
                onClick={logout}
                className="bg-blue-700 hover:bg-blue-800 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Logout
              </button>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center sm:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-blue-100 hover:text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {/* Hamburger icon */}
              {!mobileMenuOpen ? (
                <svg
                  className="block h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              ) : (
                <svg
                  className="block h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="sm:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <Link
              to="/dashboard"
              className={`block ${navLinkClass('/dashboard')}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Dashboard
            </Link>
            <Link
              to="/admin"
              className={`block ${navLinkClass('/admin')}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              API Keys
            </Link>
          </div>
          <div className="pt-4 pb-3 border-t border-blue-600">
            <div className="flex items-center px-4">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-blue-700 flex items-center justify-center text-white font-bold">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </div>
              </div>
              <div className="ml-3">
                <div className="text-base font-medium text-white">
                  {user?.name || 'User'}
                </div>
                <div className="text-sm font-medium text-blue-200">{user?.email}</div>
              </div>
            </div>
            <div className="mt-3 px-2">
              <button
                onClick={logout}
                className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-blue-100 hover:text-white hover:bg-blue-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
