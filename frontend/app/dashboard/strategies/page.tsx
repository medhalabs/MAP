'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { apiClient } from '@/lib/api'
import { PlusIcon, PlayIcon, StopIcon, EyeIcon } from '@heroicons/react/24/outline'

interface Strategy {
  id: number
  name: string
  description: string | null
  is_active: boolean
  created_at: string
}

interface StrategyRun {
  id: number
  strategy_id: number
  status: string
  trading_mode: string
  created_at: string
}

export default function StrategiesPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [strategyRuns, setStrategyRuns] = useState<Record<number, StrategyRun[]>>({})
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newStrategy, setNewStrategy] = useState({ name: '', description: '', config: '{}' })

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user) {
      loadStrategies()
    }
  }, [user])

  const loadStrategies = async () => {
    try {
      setLoading(true)
      const data = await apiClient.get('/api/strategies')
      setStrategies(data)
      
      // Load runs for each strategy
      const runsMap: Record<number, StrategyRun[]> = {}
      for (const strategy of data) {
        try {
          const runs = await apiClient.get(`/api/strategies/runs?strategy_id=${strategy.id}`)
          runsMap[strategy.id] = runs
        } catch (error) {
          console.error(`Failed to load runs for strategy ${strategy.id}:`, error)
          runsMap[strategy.id] = []
        }
      }
      setStrategyRuns(runsMap)
    } catch (error) {
      console.error('Failed to load strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateStrategy = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiClient.post('/api/strategies', {
        name: newStrategy.name,
        description: newStrategy.description || null,
        config: JSON.parse(newStrategy.config),
        is_active: true,
      })
      setShowCreateModal(false)
      setNewStrategy({ name: '', description: '', config: '{}' })
      loadStrategies()
    } catch (error: any) {
      alert(`Failed to create strategy: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleStartStrategy = async (strategyId: number) => {
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
      loadStrategies()
    } catch (error: any) {
      alert(`Failed to start strategy: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleStopStrategy = async (runId: number) => {
    try {
      await apiClient.post(`/api/strategies/runs/${runId}/stop`)
      loadStrategies()
    } catch (error: any) {
      alert(`Failed to stop strategy: ${error.response?.data?.detail || error.message}`)
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
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Strategies</h2>
            <p className="mt-2 text-gray-600">Manage your trading strategies</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Strategy
          </button>
        </div>

        {strategies.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 text-lg mb-4">No strategies yet</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Your First Strategy
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {strategies.map((strategy) => {
              const runs = strategyRuns[strategy.id] || []
              const activeRun = runs.find(r => r.status === 'running')
              
              return (
                <div key={strategy.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{strategy.name}</h3>
                      {strategy.description && (
                        <p className="text-sm text-gray-600 mt-1">{strategy.description}</p>
                      )}
                    </div>
                    <span className={`px-2 py-1 text-xs rounded ${strategy.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {strategy.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-600">
                      Created: {new Date(strategy.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Runs: {runs.length} total, {runs.filter(r => r.status === 'running').length} active
                    </p>
                  </div>

                  <div className="flex space-x-2">
                    {activeRun ? (
                      <button
                        onClick={() => handleStopStrategy(activeRun.id)}
                        className="flex-1 flex items-center justify-center px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        <StopIcon className="h-4 w-4 mr-2" />
                        Stop
                      </button>
                    ) : (
                      <button
                        onClick={() => handleStartStrategy(strategy.id)}
                        className="flex-1 flex items-center justify-center px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        <PlayIcon className="h-4 w-4 mr-2" />
                        Start
                      </button>
                    )}
                    <Link
                      href={`/dashboard/strategies/${strategy.id}`}
                      className="flex items-center justify-center px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </Link>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Create Strategy Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-xl font-bold mb-4">Create Strategy</h3>
              <form onSubmit={handleCreateStrategy}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    value={newStrategy.name}
                    onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={newStrategy.description}
                    onChange={(e) => setNewStrategy({ ...newStrategy, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows={3}
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Config (JSON)
                  </label>
                  <textarea
                    value={newStrategy.config}
                    onChange={(e) => setNewStrategy({ ...newStrategy, config: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                    rows={4}
                    required
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Create
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
