/**
 * Admin Page
 *
 * Manage API keys for agents.
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiKeysApi, APIKey, APIKeyCreated } from '@/services/api'

export default function Admin() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showCreateForm, setShowCreateForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)
  const [createdKey, setCreatedKey] = useState<APIKeyCreated | null>(null)

  useEffect(() => {
    loadApiKeys()
  }, [])

  const loadApiKeys = async () => {
    setLoading(true)
    setError('')

    try {
      const keys = await apiKeysApi.list()
      setApiKeys(keys)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load API keys')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setError('')

    try {
      const newKey = await apiKeysApi.create(name, description || undefined)
      setCreatedKey(newKey)
      setName('')
      setDescription('')
      setShowCreateForm(false)
      await loadApiKeys()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create API key')
    } finally {
      setCreating(false)
    }
  }

  const handleRevoke = async (id: string) => {
    if (!confirm('Are you sure you want to revoke this API key?')) return

    try {
      await apiKeysApi.update(id, { is_active: false })
      await loadApiKeys()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to revoke API key')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container-mobile py-4">
          <Link to="/dashboard" className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">API Key Management</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-mobile py-8">
        {/* Created Key Alert */}
        {createdKey && (
          <div className="mb-6 card bg-green-50 border border-green-200">
            <h3 className="text-lg font-semibold text-green-900 mb-2">API Key Created!</h3>
            <p className="text-sm text-green-800 mb-3">
              Save this key now - it won't be shown again!
            </p>
            <div className="bg-white rounded p-3 border border-green-300">
              <code className="text-sm font-mono break-all select-all">{createdKey.key}</code>
            </div>
            <button
              onClick={() => setCreatedKey(null)}
              className="mt-3 text-sm text-green-700 hover:text-green-800"
            >
              I've saved it, dismiss this
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Create Button */}
        {!showCreateForm && (
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary mb-6"
          >
            Create New API Key
          </button>
        )}

        {/* Create Form */}
        {showCreateForm && (
          <div className="card mb-6">
            <h2 className="text-lg font-semibold mb-4">Create New API Key</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Name *
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input mt-1"
                  placeholder="my-agent"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  id="description"
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="input mt-1"
                  placeholder="What this API key is for..."
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={creating}
                  className="btn-primary"
                >
                  {creating ? 'Creating...' : 'Create API Key'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Loading */}
        {loading && <p className="text-gray-600">Loading API keys...</p>}

        {/* API Keys List */}
        {!loading && apiKeys.length === 0 && (
          <div className="card text-center py-12">
            <p className="text-gray-600">No API keys found</p>
            <p className="text-sm text-gray-500 mt-2">Create one to get started</p>
          </div>
        )}

        {!loading && apiKeys.length > 0 && (
          <div className="space-y-4">
            {apiKeys.map((key) => (
              <div key={key.id} className="card">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="text-lg font-semibold">{key.name}</h3>
                    {key.description && (
                      <p className="text-sm text-gray-600 mt-1">{key.description}</p>
                    )}
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      key.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {key.is_active ? 'Active' : 'Revoked'}
                  </span>
                </div>

                <div className="text-sm text-gray-500 space-y-1">
                  <div>Created: {formatDate(key.created_at)}</div>
                  <div className="font-mono text-xs break-all">ID: {key.id}</div>
                </div>

                {key.is_active && (
                  <button
                    onClick={() => handleRevoke(key.id)}
                    className="mt-3 text-sm text-red-600 hover:text-red-700"
                  >
                    Revoke Key
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
