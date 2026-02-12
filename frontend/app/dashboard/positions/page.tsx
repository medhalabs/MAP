'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { apiClient } from '@/lib/api'

interface Position {
  id: number
  symbol: string
  quantity: number
  average_price: number | null
  current_price: number | null
  unrealized_pnl: number | null
  created_at: string
  updated_at: string
}

export default function PositionsPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user) {
      loadPositions()
      // Refresh every 10 seconds
      const interval = setInterval(loadPositions, 10000)
      return () => clearInterval(interval)
    }
  }, [user])

  const loadPositions = async () => {
    try {
      setLoading(true)
      const data = await apiClient.get('/api/positions')
      setPositions(data)
    } catch (error) {
      console.error('Failed to load positions:', error)
    } finally {
      setLoading(false)
    }
  }

  const totalUnrealizedPnl = positions.reduce((sum, pos) => sum + (pos.unrealized_pnl || 0), 0)

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
                <Link href="/dashboard/positions" className="text-primary-600 font-medium border-b-2 border-primary-600 pb-4">
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
          <h2 className="text-3xl font-bold text-gray-900">Positions</h2>
          <p className="mt-2 text-gray-600">Current open positions</p>
        </div>

        {/* Summary Card */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Positions</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{positions.length}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total Quantity</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {positions.reduce((sum, pos) => sum + Math.abs(pos.quantity), 0)}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total Unrealized P&L</p>
              <p className={`mt-2 text-3xl font-bold ${totalUnrealizedPnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ₹{totalUnrealizedPnl.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        {/* Positions Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {positions.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-gray-500 text-lg">No open positions</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Current Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Unrealized P&L
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Updated
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {positions.map((position) => (
                    <tr key={position.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {position.symbol}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className={`font-semibold ${position.quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {position.quantity > 0 ? '+' : ''}{position.quantity}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {position.average_price ? `₹${position.average_price.toFixed(2)}` : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {position.current_price ? `₹${position.current_price.toFixed(2)}` : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`font-semibold ${(position.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {position.unrealized_pnl !== null ? `₹${position.unrealized_pnl.toFixed(2)}` : 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(position.updated_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

