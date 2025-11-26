/**
 * usePolling Hook
 *
 * Custom hook for polling an async function at regular intervals.
 * Automatically pauses when tab is not visible (Page Visibility API).
 */

import { useEffect, useRef, useState } from 'react'

interface UsePollingOptions<T> {
  /**
   * Function to call on each poll
   */
  fn: () => Promise<T>

  /**
   * Polling interval in milliseconds
   * @default 10000 (10 seconds)
   */
  interval?: number

  /**
   * Whether to start polling immediately
   * @default true
   */
  enabled?: boolean

  /**
   * Callback when new data is available
   */
  onUpdate?: (data: T) => void
}

export function usePolling<T>({
  fn,
  interval = 10000,
  enabled = true,
  onUpdate,
}: UsePollingOptions<T>) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isPolling, setIsPolling] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const isVisibleRef = useRef(true)

  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      isVisibleRef.current = document.visibilityState === 'visible'

      if (isVisibleRef.current && enabled) {
        // Tab became visible, resume polling
        startPolling()
      } else {
        // Tab hidden, pause polling
        stopPolling()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [enabled])

  const poll = async () => {
    if (!isVisibleRef.current) return

    try {
      setIsPolling(true)
      const result = await fn()
      setData(result)
      setError(null)

      if (onUpdate) {
        onUpdate(result)
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Polling failed'))
    } finally {
      setIsPolling(false)
    }
  }

  const startPolling = () => {
    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    // Poll immediately
    poll()

    // Then poll at interval
    intervalRef.current = setInterval(poll, interval)
  }

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  // Start/stop polling based on enabled flag
  useEffect(() => {
    if (enabled && isVisibleRef.current) {
      startPolling()
    } else {
      stopPolling()
    }

    return () => {
      stopPolling()
    }
  }, [enabled, interval])

  return {
    data,
    error,
    isPolling,
    refresh: poll,
  }
}
