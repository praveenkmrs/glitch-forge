/**
 * Dashboard Page
 *
 * Shows list of consultation requests with filtering and auto-refresh polling.
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { requestsApi, ConsultationRequest } from '@/services/api'
import { usePolling } from '@/hooks/usePolling'

export default function Dashboard() {
  const [requests, setRequests] = useState<ConsultationRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState<string>('pending')
  const [total, setTotal] = useState(0)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const [hasNewUpdates, setHasNewUpdates] = useState(false)

  // Load initial data
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

      // Update last updated timestamp for differential polling
      if (data.items.length > 0) {
        const mostRecent = data.items.reduce((latest, req) => {
          return new Date(req.updated_at) > new Date(latest) ? req.updated_at : latest
        }, data.items[0].updated_at)
        setLastUpdated(mostRecent)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load requests')
    } finally {
      setLoading(false)
    }
  }

  // Polling for updates (differential)
  const { isPolling } = usePolling({
    fn: async () => {
      if (!lastUpdated) return null

      // Only fetch requests updated after last poll
      const data = await requestsApi.list(filter || undefined, 20, 0, lastUpdated)

      if (data.items.length > 0) {
        // New updates found!
        setHasNewUpdates(true)

        // Update last updated timestamp
        const mostRecent = data.items.reduce((latest, req) => {
          return new Date(req.updated_at) > new Date(latest) ? req.updated_at : latest
        }, data.items[0].updated_at)
        setLastUpdated(mostRecent)
      }

      return data
    },
    interval: 10000, // Poll every 10 seconds
    enabled: !!lastUpdated, // Only poll after initial load
  })

  const refreshNow = () => {
    setHasNewUpdates(false)
    loadRequests()
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
    <div className="container-mobile py-8">
      {/* Update Notification Banner */}
      {hasNewUpdates && (
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4 flex justify-between items-center">
          <div className="flex items-center">
            <svg
              className="h-5 w-5 text-blue-400 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-sm text-blue-800">
              New updates available{isPolling && ' (checking for updates...)'}
            </p>
          </div>
          <button
            onClick={refreshNow}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            Refresh Now
          </button>
        </div>
      )}

      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Consultation Requests</h1>
        <p className="text-sm text-gray-600 mt-1">
          {total} total request{total !== 1 ? 's' : ''}
        </p>
      </div>
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
    </div>
  )
}
