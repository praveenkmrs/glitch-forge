/**
 * Main Application Component
 *
 * This is a minimal starter. We'll add:
 * - React Router for navigation
 * - React Query for server state
 * - Authentication context
 * - Error boundaries
 */

import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container-mobile py-4">
          <h1 className="text-2xl font-bold text-primary-600">Glitch Forge HITL</h1>
          <p className="text-sm text-gray-600">Human-in-the-Loop Agent Consultation</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-mobile py-8">
        <div className="card max-w-md mx-auto text-center">
          <h2 className="text-xl font-semibold mb-4">Welcome to Glitch Forge</h2>
          <p className="text-gray-600 mb-6">
            This is a starter template. We'll build the HITL interface step by step.
          </p>

          {/* Demo counter - mobile-first button */}
          <div className="space-y-4">
            <div className="text-4xl font-bold text-primary-600">{count}</div>
            <button
              onClick={() => setCount((count) => count + 1)}
              className="btn-primary w-full sm:w-auto"
            >
              Increment Counter
            </button>
            <p className="text-sm text-gray-500">
              Click the button to test the mobile-first styling
            </p>
          </div>
        </div>

        {/* Feature Grid - Mobile responsive */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className="card">
            <h3 className="font-semibold text-lg mb-2">🚀 Fast</h3>
            <p className="text-sm text-gray-600">Built with Vite for lightning-fast development</p>
          </div>
          <div className="card">
            <h3 className="font-semibold text-lg mb-2">📱 Mobile-First</h3>
            <p className="text-sm text-gray-600">Optimized for mobile devices with TailwindCSS</p>
          </div>
          <div className="card">
            <h3 className="font-semibold text-lg mb-2">🔒 Secure</h3>
            <p className="text-sm text-gray-600">JWT authentication with refresh tokens</p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container-mobile py-4 mt-8 text-center text-sm text-gray-500">
        <p>Glitch Forge v0.1.0 - Production-ready HITL application</p>
      </footer>
    </div>
  )
}

export default App
