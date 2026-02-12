'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { apiClient } from '@/lib/api'
import { ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/outline'

interface RiskEvent {
  id: number
  event_type: string
  severity: string
  message: string
  event_metadata: Record<string, any>
  created_at: string
}

interface RiskStats {
  today_events: number
  critical_count: number
  warning_count: number
}

export default function RiskPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const [events, setEvents] = useState<RiskEvent[]>([])
  const [stats, setStats] = useState<RiskStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState({ severity: '' })

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user) {
      loadRiskData()
      // Refresh every 10 seconds
      const interval = setInterval(loadRiskData, 10000)
      return () => clearInterval(interval)
    }
  }, [user, filter])

  const loadRiskData = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filter.severity) params.append('severity', filter.severity)
      
      const [eventsData, statsData] = await Promise.all([
        apiClient.get(`/api/risk?${params.toString()}`),
        apiClient.get('/api/risk/stats'),
      ])
      setEvents(eventsData)
      setStats(statsData)
    } catch (error) {
      console.error('Failed to load risk data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircleIcon className="h-5 w-5 text-red-600" />
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />
      default:
        return null
    }
  }

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link href="/dashboard" className="text-xl font-bold text-gray-900">
                MedhaAlgoPilot
              </Link>
              <div className="flex space-x-4">
                <Link href="/dashboard" className="text-gray-700 hover:text-gray-900 pb-4">
                  Dashboard
                </Link>
                <Link href="/dashboard/strategies" className="text-gray-700 hover:text-gray-900 pb-4">
                  Strategies
                </Link>
                <Link href="/dashboard/orders" className="text-gray-700 hover:text-gray-900 pb-4">
                  Orders
                </Link>
                <Link href="/dashboard/positions" className="text-gray-700 hover:text-gray-900 pb-4">
                  Positions
                </Link>
                <Link href="/dashboard/risk" className="text-primary-600 font-medium border-b-2 border-primary-600 pb-4">
                  Risk Monitor
                </Link>
                <Link href="/dashboard/settings" className="text-gray-700 hover:text-gray-900 pb-4">
                  Settings
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user.username}</span>
              <button
                onClick={() => {
                  localStorage.removeItem('access_token')
                  router.push('/auth/login')
                }}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Risk Monitor</h2>
          <p className="mt-2 text-gray-600">Risk events and alerts</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600">Events Today</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.today_events}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600">Critical Events</p>
              <p className="mt-2 text-3xl font-bold text-red-600">{stats.critical_count}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600">Warnings</p>
              <p className="mt-2 text-3xl font-bold text-yellow-600">{stats.warning_count}</p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
              <select
                value={filter.severity}
                onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All</option>
                <option value="critical">Critical</option>
                <option value="warning">Warning</option>
                <option value="info">Info</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilter({ severity: '' })}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Clear Filter
              </button>
            </div>
          </div>
        </div>

        {/* Risk Events */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {events.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-gray-500 text-lg">No risk events found</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {events.map((event) => (
                <div
                  key={event.id}
                  className={`p-6 border-l-4 ${getSeverityColor(event.severity)}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      {getSeverityIcon(event.severity) && (
                        <div className="flex-shrink-0 mt-0.5">
                          {getSeverityIcon(event.severity)}
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(event.severity)}`}>
                            {event.severity.toUpperCase()}
                          </span>
                          <span className="text-sm font-medium text-gray-600">{event.event_type}</span>
                        </div>
                        <p className="text-sm text-gray-900 mt-1">{event.message}</p>
                        {event.event_metadata && Object.keys(event.event_metadata).length > 0 && (
                          <div className="mt-2 text-xs text-gray-500 font-mono bg-gray-50 p-2 rounded">
                            {JSON.stringify(event.event_metadata, null, 2)}
                          </div>
                        )}
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(event.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

