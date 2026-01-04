'use client'

import Link from 'next/link'
import { 
  ArrowRightIcon, 
  ChartBarIcon, 
  ShieldCheckIcon, 
  BoltIcon, 
  CpuChipIcon, 
  ClockIcon 
} from '@heroicons/react/24/outline'

export default function LandingPage() {
  const features = [
    {
      name: 'Multi-Strategy Trading',
      description: 'Run multiple trading strategies simultaneously with independent risk management and capital allocation.',
      icon: ChartBarIcon,
    },
    {
      name: 'Real-Time Monitoring',
      description: 'Live P&L tracking, order updates, and strategy performance metrics via WebSocket connections.',
      icon: BoltIcon,
    },
    {
      name: 'Risk Management',
      description: 'Built-in risk engine with configurable rules: daily loss limits, position limits, and capital allocation.',
      icon: ShieldCheckIcon,
    },
    {
      name: 'Paper & Live Trading',
      description: 'Test strategies in paper trading mode before going live. Seamless switch between modes.',
      icon: CpuChipIcon,
    },
    {
      name: 'Full Audit Trail',
      description: 'Complete immutable record of all orders, trades, and risk events for compliance and analysis.',
      icon: ClockIcon,
    },
    {
      name: 'Multi-Tenant Architecture',
      description: 'Organizations can manage multiple users, strategies, and broker accounts with role-based access.',
      icon: ShieldCheckIcon,
    },
  ]

  const benefits = [
    'Event-driven architecture for low latency',
    'Stateless strategies reusable for backtesting',
    'Pluggable broker integration (Dhan, and more)',
    'Production-grade error handling and logging',
    'PostgreSQL as single source of truth',
    'Clean architecture for easy maintenance',
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  MedhaAlgoPilot
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/auth/login"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/auth/register"
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-md text-sm font-medium hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            <h1 className="text-5xl sm:text-6xl font-extrabold text-gray-900 tracking-tight">
              Algorithmic Trading
              <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Made Simple
              </span>
            </h1>
            <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
              Production-grade algorithmic trading platform with built-in risk management, 
              real-time monitoring, and multi-tenant support. Deploy strategies with confidence.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/auth/register"
                className="inline-flex items-center px-8 py-4 border border-transparent text-base font-medium rounded-md text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all"
              >
                Start Free Trial
                <ArrowRightIcon className="ml-2 -mr-1 h-5 w-5" />
              </Link>
              <Link
                href="#features"
                className="inline-flex items-center px-8 py-4 border-2 border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                Learn More
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Everything you need to trade algorithmically
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Built for traders, developers, and organizations who demand reliability and control.
            </p>
          </div>

          <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div
                key={feature.name}
                className="relative bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100"
              >
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                  <feature.icon className="h-6 w-6" aria-hidden="true" />
                </div>
                <h3 className="mt-6 text-lg font-medium text-gray-900">{feature.name}</h3>
                <p className="mt-2 text-base text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="py-24 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8">
            <div>
              <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                Built for Production
              </h2>
              <p className="mt-4 text-lg text-gray-600">
                MedhaAlgoPilot is designed from the ground up with production-grade architecture, 
                ensuring reliability, scalability, and maintainability.
              </p>
              <ul className="mt-8 space-y-4">
                {benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-6 w-6 rounded-full bg-gradient-to-r from-blue-600 to-purple-600">
                        <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    </div>
                    <p className="ml-3 text-base text-gray-700">{benefit}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div className="mt-12 lg:mt-0">
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Architecture Highlights</h3>
                <div className="space-y-4">
                  <div className="border-l-4 border-blue-600 pl-4">
                    <h4 className="font-semibold text-gray-900">Clean Architecture</h4>
                    <p className="text-gray-600 text-sm mt-1">Four distinct layers: API, Trading Engine, Risk Engine, Broker Integration</p>
                  </div>
                  <div className="border-l-4 border-purple-600 pl-4">
                    <h4 className="font-semibold text-gray-900">Event-Driven</h4>
                    <p className="text-gray-600 text-sm mt-1">Asynchronous, non-blocking operations for optimal performance</p>
                  </div>
                  <div className="border-l-4 border-blue-600 pl-4">
                    <h4 className="font-semibold text-gray-900">Multi-Tenant</h4>
                    <p className="text-gray-600 text-sm mt-1">Organizations can manage multiple users and strategies with isolation</p>
                  </div>
                  <div className="border-l-4 border-purple-600 pl-4">
                    <h4 className="font-semibold text-gray-900">Extensible</h4>
                    <p className="text-gray-600 text-sm mt-1">Easy to add new brokers, strategies, and risk rules</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tech Stack Section */}
      <div className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Modern Tech Stack
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Built with best-in-class technologies for performance and reliability.
            </p>
          </div>
          <div className="mt-12 grid grid-cols-2 gap-8 sm:grid-cols-4">
            {[
              { name: 'FastAPI', desc: 'High-performance Python API' },
              { name: 'Next.js', desc: 'React framework' },
              { name: 'PostgreSQL', desc: 'Reliable database' },
              { name: 'TypeScript', desc: 'Type-safe frontend' },
            ].map((tech) => (
              <div key={tech.name} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{tech.name}</div>
                <div className="mt-2 text-sm text-gray-600">{tech.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
              Ready to start trading algorithmically?
            </h2>
            <p className="mt-4 text-xl text-blue-100">
              Join organizations already using MedhaAlgoPilot to automate their trading strategies.
            </p>
            <div className="mt-8">
              <Link
                href="/auth/register"
                className="inline-flex items-center px-8 py-4 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50 shadow-lg hover:shadow-xl transition-all"
              >
                Get Started Free
                <ArrowRightIcon className="ml-2 -mr-1 h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              MedhaAlgoPilot
            </h3>
            <p className="mt-4 text-gray-400">
              Production-grade algorithmic trading platform
            </p>
            <p className="mt-2 text-sm text-gray-500">
              © {new Date().getFullYear()} MedhaAlgoPilot. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
