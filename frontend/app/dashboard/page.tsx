'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useAuth } from '@/hooks/useAuth'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const { isConnected } = useWebSocket()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-gray-900">MedhaAlgoPilot</h1>
              <div className="flex space-x-4">
                <Link href="/dashboard" className="text-primary-600 font-medium">Dashboard</Link>
                <Link href="/dashboard/strategies" className="text-gray-700 hover:text-gray-900">Strategies</Link>
                <Link href="/dashboard/orders" className="text-gray-700 hover:text-gray-900">Orders</Link>
                <Link href="/dashboard/positions" className="text-gray-700 hover:text-gray-900">Positions</Link>
                <Link href="/dashboard/risk" className="text-gray-700 hover:text-gray-900">Risk Monitor</Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600">{user.username}</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="mt-2 text-gray-600">Account overview and trading status</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Total P&L</h3>
            <p className="mt-2 text-3xl font-bold text-green-600">₹0.00</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Active Strategies</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Open Positions</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
          </div>
        </div>
      </main>
    </div>
  )
}

