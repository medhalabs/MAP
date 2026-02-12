'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { apiClient } from '@/lib/api'
import { 
  Cog6ToothIcon, 
  BuildingOfficeIcon, 
  UserIcon, 
  CreditCardIcon,
  ShieldCheckIcon,
  BellIcon,
  KeyIcon,
  PlusIcon,
  TrashIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/react/24/outline'

interface TenantSettings {
  name: string
  slug: string
  subscription_tier: string
  max_users: number
  max_strategies: number
  max_daily_loss: number | null
  max_open_positions: number | null
  max_position_size: number | null
  risk_notifications_enabled: boolean
  email_notifications: boolean
}

interface UserSettings {
  email_notifications: boolean
  risk_alerts: boolean
  strategy_notifications: boolean
}

interface BrokerAccount {
  id: number
  broker_name: string
  account_id: string
  is_default: boolean
  is_active: boolean
  created_at: string
  available_balance?: number | null
}

export default function SettingsPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const [activeTab, setActiveTab] = useState<'general' | 'broker' | 'risk' | 'notifications'>('general')
  const [tenantSettings, setTenantSettings] = useState<TenantSettings | null>(null)
  const [userSettings, setUserSettings] = useState<UserSettings | null>(null)
  const [brokerAccounts, setBrokerAccounts] = useState<BrokerAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showAddBroker, setShowAddBroker] = useState(false)
  const [newBroker, setNewBroker] = useState({
    broker_name: 'dhan',
    account_id: '',
    api_key: '',
    api_secret: '',
    is_default: false,
  })

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user) {
      loadSettings()
    }
  }, [user])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const [tenantData, userData, brokerData] = await Promise.all([
        apiClient.get('/api/settings/tenant'),
        apiClient.get('/api/settings/user'),
        apiClient.get('/api/broker-accounts'),
      ])
      setTenantSettings(tenantData)
      setUserSettings(userData)
      setBrokerAccounts(brokerData)
    } catch (error) {
      console.error('Failed to load settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveTenantSettings = async () => {
    if (!tenantSettings) return
    
    try {
      setSaving(true)
      await apiClient.put('/api/settings/tenant', {
        name: tenantSettings.name,
        max_daily_loss: tenantSettings.max_daily_loss,
        max_open_positions: tenantSettings.max_open_positions,
        max_position_size: tenantSettings.max_position_size,
        risk_notifications_enabled: tenantSettings.risk_notifications_enabled,
        email_notifications: tenantSettings.email_notifications,
      })
      alert('Settings saved successfully!')
    } catch (error: any) {
      alert(`Failed to save settings: ${error.response?.data?.detail || error.message}`)
    } finally {
      setSaving(false)
    }
  }

  const handleSaveUserSettings = async () => {
    if (!userSettings) return
    
    try {
      setSaving(true)
      await apiClient.put('/api/settings/user', userSettings)
      alert('Settings saved successfully!')
    } catch (error: any) {
      alert(`Failed to save settings: ${error.response?.data?.detail || error.message}`)
    } finally {
      setSaving(false)
    }
  }

  const handleAddBroker = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSaving(true)
      // The backend will test the connection automatically
      await apiClient.post('/api/broker-accounts', newBroker)
      setShowAddBroker(false)
      setNewBroker({
        broker_name: 'dhan',
        account_id: '',
        api_key: '',
        api_secret: '',
        is_default: false,
      })
      loadSettings()
      alert('Broker account added and connection verified successfully!')
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message
      alert(`Failed to add broker account: ${errorMessage}\n\nPlease check:\n- Account ID is correct\n- API Key is correct\n- Access Token is valid and not expired\n- You have internet connectivity`)
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteBroker = async (accountId: number) => {
    if (!confirm('Are you sure you want to delete this broker account?')) {
      return
    }
    
    try {
      await apiClient.delete(`/api/broker-accounts/${accountId}`)
      loadSettings()
      alert('Broker account deleted successfully!')
    } catch (error: any) {
      alert(`Failed to delete broker account: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleToggleActive = async (accountId: number, currentStatus: boolean) => {
    try {
      await apiClient.patch(`/api/broker-accounts/${accountId}/toggle-active`)
      loadSettings()
      // No alert needed - the status badge will update automatically
    } catch (error: any) {
      alert(`Failed to ${currentStatus ? 'pause' : 'activate'} broker account: ${error.response?.data?.detail || error.message}`)
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
                <Link href="/dashboard/risk" className="text-gray-700 hover:text-gray-900 pb-4">
                  Risk Monitor
                </Link>
                <Link href="/dashboard/settings" className="text-primary-600 font-medium border-b-2 border-primary-600 pb-4">
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
          <h2 className="text-3xl font-bold text-gray-900">Settings</h2>
          <p className="mt-2 text-gray-600">Manage your application settings and preferences</p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('general')}
                className={`py-4 px-6 border-b-2 font-medium text-sm ${
                  activeTab === 'general'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BuildingOfficeIcon className="h-5 w-5 inline mr-2" />
                General
              </button>
              <button
                onClick={() => setActiveTab('broker')}
                className={`py-4 px-6 border-b-2 font-medium text-sm ${
                  activeTab === 'broker'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <KeyIcon className="h-5 w-5 inline mr-2" />
                Broker Accounts
              </button>
              <button
                onClick={() => setActiveTab('risk')}
                className={`py-4 px-6 border-b-2 font-medium text-sm ${
                  activeTab === 'risk'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <ShieldCheckIcon className="h-5 w-5 inline mr-2" />
                Risk Management
              </button>
              <button
                onClick={() => setActiveTab('notifications')}
                className={`py-4 px-6 border-b-2 font-medium text-sm ${
                  activeTab === 'notifications'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BellIcon className="h-5 w-5 inline mr-2" />
                Notifications
              </button>
            </nav>
          </div>
        </div>

        {/* General Settings */}
        {activeTab === 'general' && tenantSettings && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Organization Settings</h3>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organization Name
                </label>
                <input
                  type="text"
                  value={tenantSettings.name}
                  onChange={(e) => setTenantSettings({ ...tenantSettings, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Subscription Tier
                  </label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg">
                    <span className="text-sm text-gray-600 capitalize">{tenantSettings.subscription_tier}</span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Organization Slug
                  </label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg">
                    <span className="text-sm text-gray-600">{tenantSettings.slug}</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Users
                  </label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg">
                    <span className="text-sm text-gray-600">{tenantSettings.max_users}</span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Strategies
                  </label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg">
                    <span className="text-sm text-gray-600">{tenantSettings.max_strategies}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <button
                  onClick={handleSaveTenantSettings}
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Broker Accounts */}
        {activeTab === 'broker' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-medium text-gray-900">Broker Accounts</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={async () => {
                      try {
                        setLoading(true)
                        const brokerData = await apiClient.get('/api/broker-accounts')
                        setBrokerAccounts(brokerData)
                        alert('Balances refreshed successfully!')
                      } catch (error: any) {
                        console.error('Failed to refresh balances:', error)
                        alert(`Failed to refresh balances: ${error.response?.data?.detail || error.message}`)
                      } finally {
                        setLoading(false)
                      }
                    }}
                    disabled={loading}
                    className="flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Refresh balances"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {loading ? 'Refreshing...' : 'Refresh'}
                  </button>
                  <button
                    onClick={() => setShowAddBroker(true)}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Add Broker Account
                  </button>
                </div>
              </div>

              {brokerAccounts.length === 0 ? (
                <div className="text-center py-12">
                  <KeyIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">No broker accounts configured</p>
                  <button
                    onClick={() => setShowAddBroker(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Add Your First Broker Account
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {brokerAccounts.map((account) => (
                    <div
                      key={account.id}
                      className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center space-x-2 mb-2">
                            <h4 className="font-medium text-gray-900 capitalize">{account.broker_name}</h4>
                            {account.is_default && (
                              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                                Default
                              </span>
                            )}
                            {account.is_active ? (
                              <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                                Active
                              </span>
                            ) : (
                              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                                Inactive
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600">Account ID: {account.account_id}</p>
                          {account.available_balance !== null && account.available_balance !== undefined ? (
                            <div className="mt-2 p-2 bg-green-50 rounded border border-green-200">
                              <p className="text-sm font-semibold text-green-700">
                                Available Balance: ₹{typeof account.available_balance === 'number' 
                                  ? account.available_balance.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                                  : parseFloat(account.available_balance.toString()).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                              </p>
                            </div>
                          ) : (
                            <div className="mt-2">
                              <p className="text-xs text-gray-400 mt-1 italic">Balance: Not loaded</p>
                              <button
                                onClick={async () => {
                                  try {
                                    const response = await apiClient.post(`/api/broker-accounts/${account.id}/refresh-balance`)
                                    // Update the account in the list
                                    setBrokerAccounts(prev => prev.map(acc => 
                                      acc.id === account.id 
                                        ? { ...acc, available_balance: response.available_balance }
                                        : acc
                                    ))
                                    alert(`Balance refreshed: ₹${response.available_balance.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`)
                                  } catch (error: any) {
                                    alert(`Failed to refresh balance: ${error.response?.data?.detail || error.message}`)
                                  }
                                }}
                                className="mt-1 text-xs text-blue-600 hover:text-blue-800 underline"
                              >
                                Click to load balance
                              </button>
                            </div>
                          )}
                          <p className="text-xs text-gray-500 mt-1">
                            Added: {new Date(account.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleToggleActive(account.id, account.is_active)}
                            className={`p-2 rounded transition-colors ${
                              account.is_active
                                ? 'text-orange-600 hover:bg-orange-50'
                                : 'text-green-600 hover:bg-green-50'
                            }`}
                            title={account.is_active ? 'Pause account' : 'Activate account'}
                          >
                            {account.is_active ? (
                              <PauseIcon className="h-5 w-5" />
                            ) : (
                              <PlayIcon className="h-5 w-5" />
                            )}
                          </button>
                          <button
                            onClick={() => handleDeleteBroker(account.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded"
                            title="Delete account"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Add Broker Modal */}
            {showAddBroker && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-6 w-full max-w-md">
                  <h3 className="text-xl font-bold mb-4">Add Broker Account</h3>
                  <form onSubmit={handleAddBroker}>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Broker
                        </label>
                        <select
                          value={newBroker.broker_name}
                          onChange={(e) => setNewBroker({ ...newBroker, broker_name: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="dhan">Dhan</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Account ID
                        </label>
                        <input
                          type="text"
                          value={newBroker.account_id}
                          onChange={(e) => setNewBroker({ ...newBroker, account_id: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          API Key
                        </label>
                        <input
                          type="password"
                          value={newBroker.api_key}
                          onChange={(e) => setNewBroker({ ...newBroker, api_key: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {newBroker.broker_name === 'dhan' ? 'Access Token' : 'API Secret'}
                        </label>
                        <input
                          type="password"
                          value={newBroker.api_secret}
                          onChange={(e) => setNewBroker({ ...newBroker, api_secret: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          required
                          placeholder={newBroker.broker_name === 'dhan' ? 'Enter your Dhan access token' : 'Enter your API secret'}
                        />
                        {newBroker.broker_name === 'dhan' && (
                          <p className="mt-1 text-xs text-gray-500">
                            Get your access token from Dhan Developer Portal
                          </p>
                        )}
                      </div>
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="is_default"
                          checked={newBroker.is_default}
                          onChange={(e) => setNewBroker({ ...newBroker, is_default: e.target.checked })}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor="is_default" className="ml-2 block text-sm text-gray-900">
                          Set as default account
                        </label>
                      </div>
                    </div>
                    <div className="flex space-x-3 mt-6">
                      <button
                        type="button"
                        onClick={() => setShowAddBroker(false)}
                        className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={saving}
                        className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        {saving ? 'Adding...' : 'Add Account'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Risk Management Settings */}
        {activeTab === 'risk' && tenantSettings && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Risk Management Settings</h3>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Daily Loss (₹)
                </label>
                <input
                  type="number"
                  value={tenantSettings.max_daily_loss || ''}
                  onChange={(e) => setTenantSettings({ 
                    ...tenantSettings, 
                    max_daily_loss: e.target.value ? parseFloat(e.target.value) : null 
                  })}
                  placeholder="Enter max daily loss limit"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Maximum loss allowed per day across all strategies
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Open Positions
                </label>
                <input
                  type="number"
                  value={tenantSettings.max_open_positions || ''}
                  onChange={(e) => setTenantSettings({ 
                    ...tenantSettings, 
                    max_open_positions: e.target.value ? parseInt(e.target.value) : null 
                  })}
                  placeholder="Enter max open positions"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Maximum number of open positions at any time
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Position Size (₹)
                </label>
                <input
                  type="number"
                  value={tenantSettings.max_position_size || ''}
                  onChange={(e) => setTenantSettings({ 
                    ...tenantSettings, 
                    max_position_size: e.target.value ? parseFloat(e.target.value) : null 
                  })}
                  placeholder="Enter max position size"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Maximum value of a single position
                </p>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <button
                  onClick={handleSaveTenantSettings}
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Risk Settings'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Notifications Settings */}
        {activeTab === 'notifications' && tenantSettings && userSettings && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">Organization Notifications</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-900">
                      Risk Notifications
                    </label>
                    <p className="text-xs text-gray-500">
                      Receive alerts when risk limits are breached
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={tenantSettings.risk_notifications_enabled}
                      onChange={(e) => setTenantSettings({ 
                        ...tenantSettings, 
                        risk_notifications_enabled: e.target.checked 
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-900">
                      Email Notifications
                    </label>
                    <p className="text-xs text-gray-500">
                      Receive email alerts for important events
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={tenantSettings.email_notifications}
                      onChange={(e) => setTenantSettings({ 
                        ...tenantSettings, 
                        email_notifications: e.target.checked 
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 mt-6">
                <button
                  onClick={handleSaveTenantSettings}
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Notification Settings'}
                </button>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">Personal Notifications</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-900">
                      Email Notifications
                    </label>
                    <p className="text-xs text-gray-500">
                      Receive email updates about your account
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={userSettings.email_notifications}
                      onChange={(e) => setUserSettings({ 
                        ...userSettings, 
                        email_notifications: e.target.checked 
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-900">
                      Risk Alerts
                    </label>
                    <p className="text-xs text-gray-500">
                      Get notified about risk events
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={userSettings.risk_alerts}
                      onChange={(e) => setUserSettings({ 
                        ...userSettings, 
                        risk_alerts: e.target.checked 
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-900">
                      Strategy Notifications
                    </label>
                    <p className="text-xs text-gray-500">
                      Get notified about strategy events
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={userSettings.strategy_notifications}
                      onChange={(e) => setUserSettings({ 
                        ...userSettings, 
                        strategy_notifications: e.target.checked 
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 mt-6">
                <button
                  onClick={handleSaveUserSettings}
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Personal Settings'}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

