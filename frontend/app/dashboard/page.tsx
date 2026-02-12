'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useAuth } from '@/hooks/useAuth'
import { apiClient } from '@/lib/api'
import { ChartBarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, CurrencyDollarIcon, CubeIcon } from '@heroicons/react/24/outline'

interface DashboardStats {
  active_strategies: number
  today_orders: number
  open_positions: number
  total_pnl: number
  today_pnl: number
}

interface ActivityItem {
  id: number
  symbol: string
  status?: string
  transaction_type?: string
  quantity: number
  is_completed?: boolean
  created_at: string
}

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const { isConnected } = useWebSocket()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [activities, setActivities] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user) {
      loadDashboardData()
      // Refresh every 30 seconds
      const interval = setInterval(loadDashboardData, 30000)
      return () => clearInterval(interval)
    }
  }, [user])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [statsData, activityData] = await Promise.all([
        apiClient.get('/api/dashboard/stats'),
        apiClient.get('/api/dashboard/recent-activity'),
      ])
      setStats(statsData)
      setActivities(activityData)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
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
                <Link href="/dashboard" className="text-primary-600 font-medium border-b-2 border-primary-600 pb-4">
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
                <Link href="/dashboard/risk" className="text-gray-700 hover:text-gray-900 pb-4">
                  Risk Monitor
                </Link>
                <Link href="/dashboard/settings" className="text-gray-700 hover:text-gray-900 pb-4">
                  Settings
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} title={isConnected ? 'Connected' : 'Disconnected'} />
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
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="mt-2 text-gray-600">Trading overview and performance</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total P&L</p>
                  <p className={`mt-2 text-3xl font-bold ${stats.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ₹{stats.total_pnl.toFixed(2)}
                  </p>
                </div>
                <CurrencyDollarIcon className="h-8 w-8 text-gray-400" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Today's P&L</p>
                  <p className={`mt-2 text-3xl font-bold ${stats.today_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ₹{stats.today_pnl.toFixed(2)}
                  </p>
                </div>
                {stats.today_pnl >= 0 ? (
                  <ArrowTrendingUpIcon className="h-8 w-8 text-green-500" />
                ) : (
                  <ArrowTrendingDownIcon className="h-8 w-8 text-red-500" />
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Strategies</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{stats.active_strategies}</p>
                </div>
                <ChartBarIcon className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Open Positions</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{stats.open_positions}</p>
                </div>
                <CubeIcon className="h-8 w-8 text-purple-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Today's Orders</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{stats.today_orders}</p>
                </div>
                <ChartBarIcon className="h-8 w-8 text-indigo-500" />
              </div>
            </div>
          </div>
        )}

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Orders</h3>
            </div>
            <div className="p-6">
              {activities?.orders?.length > 0 ? (
                <div className="space-y-4">
                  {activities.orders.slice(0, 5).map((order: ActivityItem) => (
                    <div key={order.id} className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div>
                        <p className="font-medium text-gray-900">{order.symbol}</p>
                        <p className="text-sm text-gray-500">
                          {order.quantity} shares • {order.status}
                        </p>
                      </div>
                      <span className="text-xs text-gray-400">
                        {new Date(order.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No recent orders</p>
              )}
              <Link href="/dashboard/orders" className="block text-center mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium">
                View all orders →
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Trades</h3>
            </div>
            <div className="p-6">
              {activities?.trades?.length > 0 ? (
                <div className="space-y-4">
                  {activities.trades.slice(0, 5).map((trade: ActivityItem) => (
                    <div key={trade.id} className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div>
                        <p className="font-medium text-gray-900">
                          {trade.transaction_type} {trade.symbol}
                        </p>
                        <p className="text-sm text-gray-500">
                          {trade.quantity} shares • {trade.is_completed ? 'Completed' : 'Pending'}
                        </p>
                      </div>
                      <span className="text-xs text-gray-400">
                        {new Date(trade.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No recent trades</p>
              )}
              <Link href="/dashboard/trades" className="block text-center mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium">
                View all trades →
              </Link>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/dashboard/strategies"
              className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <h4 className="font-medium text-gray-900">Create Strategy</h4>
              <p className="text-sm text-gray-600 mt-1">Build and deploy a new trading strategy</p>
            </Link>
            <Link
              href="/dashboard/broker-accounts"
              className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <h4 className="font-medium text-gray-900">Add Broker Account</h4>
              <p className="text-sm text-gray-600 mt-1">Connect your broker API credentials</p>
            </Link>
            <Link
              href="/dashboard/risk"
              className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <h4 className="font-medium text-gray-900">Configure Risk Rules</h4>
              <p className="text-sm text-gray-600 mt-1">Set risk limits and monitoring</p>
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}
