/**
 * Request Detail Page
 *
 * Shows full request details and allows humans to respond.
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { requestsApi, ConsultationRequest } from '@/services/api'

export default function RequestDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [request, setRequest] = useState<ConsultationRequest | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [responding, setResponding] = useState(false)
  const [decision, setDecision] = useState<'approve' | 'reject' | 'request_changes'>('approve')
  const [comment, setComment] = useState('')
  const [submitError, setSubmitError] = useState('')

  useEffect(() => {
    loadRequest()
  }, [id])

  const loadRequest = async () => {
    if (!id) return

    setLoading(true)
    setError('')

    try {
      const data = await requestsApi.get(id)
      setRequest(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load request')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return

    setResponding(true)
    setSubmitError('')

    try {
      await requestsApi.respond(id, decision, comment || undefined)
      navigate('/dashboard')
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || 'Failed to submit response')
    } finally {
      setResponding(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading request...</p>
      </div>
    )
  }

  if (error || !request) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="card max-w-md">
          <p className="text-red-600 mb-4">{error || 'Request not found'}</p>
          <Link to="/dashboard" className="btn-primary">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const canRespond = request.state === 'pending'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container-mobile py-4">
          <Link to="/dashboard" className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">{request.title}</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-mobile py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Request Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            {request.description && (
              <div className="card">
                <h2 className="text-lg font-semibold mb-2">Description</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{request.description}</p>
              </div>
            )}

            {/* Context */}
            <div className="card">
              <h2 className="text-lg font-semibold mb-3">Context</h2>
              <div className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                  {JSON.stringify(request.context, null, 2)}
                </pre>
              </div>
            </div>

            {/* Existing Response (if any) */}
            {request.response && (
              <div className="card bg-green-50 border border-green-200">
                <h2 className="text-lg font-semibold mb-3 text-green-900">Response Submitted</h2>
                <div className="space-y-2">
                  <div>
                    <span className="text-sm font-medium text-green-900">Decision:</span>
                    <span className="ml-2 px-3 py-1 bg-green-100 rounded text-sm font-medium text-green-800">
                      {request.response.decision}
                    </span>
                  </div>
                  {request.response.comment && (
                    <div>
                      <span className="text-sm font-medium text-green-900">Comment:</span>
                      <p className="mt-1 text-sm text-green-800 whitespace-pre-wrap">
                        {request.response.comment}
                      </p>
                    </div>
                  )}
                  <div className="text-xs text-green-700">
                    Responded at: {formatDate(request.response.responded_at)}
                  </div>
                </div>
              </div>
            )}

            {/* Response Form */}
            {canRespond && (
              <div className="card">
                <h2 className="text-lg font-semibold mb-4">Submit Response</h2>

                {submitError && (
                  <div className="rounded-md bg-red-50 p-4 mb-4">
                    <p className="text-sm text-red-800">{submitError}</p>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Decision */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Decision
                    </label>
                    <div className="space-y-2">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="decision"
                          value="approve"
                          checked={decision === 'approve'}
                          onChange={(e) => setDecision(e.target.value as any)}
                          className="mr-2"
                        />
                        <span className="text-sm">Approve</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="decision"
                          value="reject"
                          checked={decision === 'reject'}
                          onChange={(e) => setDecision(e.target.value as any)}
                          className="mr-2"
                        />
                        <span className="text-sm">Reject</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="decision"
                          value="request_changes"
                          checked={decision === 'request_changes'}
                          onChange={(e) => setDecision(e.target.value as any)}
                          className="mr-2"
                        />
                        <span className="text-sm">Request Changes</span>
                      </label>
                    </div>
                  </div>

                  {/* Comment */}
                  <div>
                    <label htmlFor="comment" className="block text-sm font-medium text-gray-700">
                      Comment (optional)
                    </label>
                    <textarea
                      id="comment"
                      rows={4}
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      className="input mt-1"
                      placeholder="Add any comments or feedback..."
                    />
                  </div>

                  {/* Submit */}
                  <button
                    type="submit"
                    disabled={responding}
                    className="btn-primary w-full sm:w-auto"
                  >
                    {responding ? 'Submitting...' : 'Submit Response'}
                  </button>
                </form>
              </div>
            )}

            {!canRespond && !request.response && (
              <div className="card bg-yellow-50 border border-yellow-200">
                <p className="text-sm text-yellow-800">
                  This request is in "{request.state}" state and cannot be responded to.
                </p>
              </div>
            )}
          </div>

          {/* Right Column - Metadata */}
          <div className="space-y-6">
            {/* Status */}
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Status</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-gray-600">State:</span>
                  <span className="ml-2 font-medium">{request.state}</span>
                </div>
                <div>
                  <span className="text-gray-600">Created:</span>
                  <span className="ml-2">{formatDate(request.created_at)}</span>
                </div>
                {request.timeout_at && (
                  <div>
                    <span className="text-gray-600">Timeout:</span>
                    <span className="ml-2">{formatDate(request.timeout_at)}</span>
                  </div>
                )}
                {request.responded_at && (
                  <div>
                    <span className="text-gray-600">Responded:</span>
                    <span className="ml-2">{formatDate(request.responded_at)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Metadata */}
            {request.metadata && Object.keys(request.metadata).length > 0 && (
              <div className="card">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Metadata</h3>
                <div className="space-y-1 text-sm">
                  {Object.entries(request.metadata).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-gray-600">{key}:</span>
                      <span className="ml-2 font-mono text-xs">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ID */}
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Request ID</h3>
              <code className="text-xs bg-gray-100 px-2 py-1 rounded block break-all">
                {request.id}
              </code>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
