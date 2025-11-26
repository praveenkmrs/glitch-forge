/**
 * Dashboard Page
 *
 * Shows list of consultation requests with filtering.
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { requestsApi, ConsultationRequest } from '@/services/api'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [requests, setRequests] = useState<ConsultationRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState<string>('pending')
  const [total, setTotal] = useState(0)

  useEffect(() => {
    loadRequests()
  }, [filter])

  const loadRequests = async () => {
    setLoading(true)
    setError('')

    try {
      const data = await requestsApi.list(filter || undefined)
      setRequests(data.items)
      setTotal(data.total)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load requests')
    } finally {
      setLoading(false)
    }
  }

  const getStateColor = (state: string) => {
    switch (state) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'responded':
        return 'bg-blue-100 text-blue-800'
      case 'callback_sent':
        return 'bg-green-100 text-green-800'
      case 'callback_failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container-mobile py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-primary-600">Consultation Requests</h1>
            <p className="text-sm text-gray-600">Welcome, {user?.name || user?.email}</p>
          </div>
          <div className="flex gap-2">
            <Link to="/admin" className="btn-secondary text-sm">
              Admin
            </Link>
            <button onClick={logout} className="btn-secondary text-sm">
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-mobile py-8">
        {/* Filters */}
        <div className="mb-6 flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === '' ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            All ({total})
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'pending'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter('responded')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'responded'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Responded
          </button>
          <button
            onClick={() => setFilter('callback_sent')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'callback_sent'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Completed
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading requests...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && requests.length === 0 && (
          <div className="text-center py-12 card">
            <p className="text-gray-600">No requests found</p>
            <p className="text-sm text-gray-500 mt-2">
              {filter === 'pending'
                ? 'No pending requests at the moment'
                : 'Try changing the filter'}
            </p>
          </div>
        )}

        {/* Request List */}
        {!loading && !error && requests.length > 0 && (
          <div className="space-y-4">
            {requests.map((request) => (
              <Link
                key={request.id}
                to={`/requests/${request.id}`}
                className="card block hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{request.title}</h3>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${getStateColor(
                      request.state
                    )}`}
                  >
                    {request.state}
                  </span>
                </div>

                {request.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{request.description}</p>
                )}

                <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                  <span>Created: {formatDate(request.created_at)}</span>
                  {request.timeout_at && (
                    <span>Timeout: {formatDate(request.timeout_at)}</span>
                  )}
                  {request.metadata?.workflow_id && (
                    <span className="font-mono">{request.metadata.workflow_id}</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
