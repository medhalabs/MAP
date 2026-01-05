'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { apiClient } from '@/lib/api'
import { PlayIcon, StopIcon, ArrowLeftIcon } from '@heroicons/react/24/outline'

interface Strategy {
  id: number
  name: string
  description: string | null
  config: Record<string, any>
  is_active: boolean
  created_at: string
}

interface StrategyRun {
  id: number
  strategy_id: number
  status: string
  trading_mode: string
  config: Record<string, any>
  created_at: string
  updated_at: string
}

export default function StrategyDetailPage() {
  const router = useRouter()
  const params = useParams()
  const strategyId = parseInt(params.id as string)
  const { user, isLoading } = useAuth()
  const [strategy, setStrategy] = useState<Strategy | null>(null)
  const [runs, setRuns] = useState<StrategyRun[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user && strategyId) {
      loadStrategyData()
    }
  }, [user, strategyId])

  const loadStrategyData = async () => {
    try {
      setLoading(true)
      const [strategyData, runsData] = await Promise.all([
        apiClient.get(`/api/strategies/${strategyId}`),
        apiClient.get(`/api/strategies/runs?strategy_id=${strategyId}`),
      ])
      setStrategy(strategyData)
      setRuns(runsData)
    } catch (error) {
      console.error('Failed to load strategy data:', error)
      router.push('/dashboard/strategies')
    } finally {
      setLoading(false)
    }
  }

  const handleStartStrategy = async () => {
    try {
      const brokerAccounts = await apiClient.get('/api/broker-accounts')
      if (brokerAccounts.length === 0) {
        alert('Please add a broker account first')
        return
      }
      
      const defaultAccount = brokerAccounts.find((acc: any) => acc.is_default) || brokerAccounts[0]
      
      await apiClient.post(`/api/strategies/${strategyId}/runs`, {
        broker_account_id: defaultAccount.id,
        trading_mode: 'paper',
        config: {},
      })
      loadStrategyData()
    } catch (error: any) {
      alert(`Failed to start strategy: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleStopStrategy = async (runId: number) => {
    try {
      await apiClient.post(`/api/strategies/runs/${runId}/stop`)
      loadStrategyData()
    } catch (error: any) {
      alert(`Failed to stop strategy: ${error.response?.data?.detail || error.message}`)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800'
      case 'stopped':
        return 'bg-gray-100 text-gray-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
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

  if (!user || !strategy) {
    return null
  }

  const activeRun = runs.find(r => r.status === 'running')

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
                <Link href="/dashboard/strategies" className="text-primary-600 font-medium border-b-2 border-primary-600 pb-4">
                  Strategies
                </Link>
                <Link href="/dashboard/orders" className="text-gray-700 hover:text-gray-900 pb-4">
                  Orders
                </Link>
                <Link href="/dashboard/positions" className="text-gray-700 hover:text-gray-900 pb-4">
                  Positions
                </Link>
                <Link href="/dashboard/risk" className="text-gray-700 hover:text-gray-900 pb-4">
                  Risk Monitor
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
        <Link
          href="/dashboard/strategies"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-2" />
          Back to Strategies
        </Link>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">{strategy.name}</h2>
              {strategy.description && (
                <p className="mt-2 text-gray-600">{strategy.description}</p>
              )}
            </div>
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 text-sm rounded ${strategy.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                {strategy.is_active ? 'Active' : 'Inactive'}
              </span>
              {activeRun ? (
                <button
                  onClick={() => handleStopStrategy(activeRun.id)}
                  className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  <StopIcon className="h-5 w-5 mr-2" />
                  Stop Strategy
                </button>
              ) : (
                <button
                  onClick={handleStartStrategy}
                  className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <PlayIcon className="h-5 w-5 mr-2" />
                  Start Strategy
                </button>
              )}
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Configuration</h3>
            <pre className="bg-gray-50 p-4 rounded-lg text-xs overflow-x-auto">
              {JSON.stringify(strategy.config, null, 2)}
            </pre>
          </div>

          <div className="mt-4">
            <p className="text-sm text-gray-600">
              Created: {new Date(strategy.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Strategy Runs */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Strategy Runs</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {runs.length === 0 ? (
              <div className="p-12 text-center">
                <p className="text-gray-500">No runs yet</p>
              </div>
            ) : (
              runs.map((run) => (
                <div key={run.id} className="p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center space-x-3 mb-2">
                        <span className={`px-2 py-1 text-xs rounded ${getStatusColor(run.status)}`}>
                          {run.status}
                        </span>
                        <span className="text-sm text-gray-600">{run.trading_mode}</span>
                        <span className="text-sm font-mono text-gray-500">#{run.id}</span>
                      </div>
                      <p className="text-sm text-gray-600">
                        Started: {new Date(run.created_at).toLocaleString()}
                      </p>
                      {run.updated_at !== run.created_at && (
                        <p className="text-sm text-gray-600">
                          Updated: {new Date(run.updated_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                    {run.status === 'running' && (
                      <button
                        onClick={() => handleStopStrategy(run.id)}
                        className="flex items-center px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                      >
                        <StopIcon className="h-4 w-4 mr-1" />
                        Stop
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

