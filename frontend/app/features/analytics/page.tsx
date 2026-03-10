import Link from 'next/link'
import { ArrowLeft, BarChart, TrendingUp, PieChart, Activity, CheckCircle2, LineChart } from 'lucide-react'

export default function AnalyticsPage() {
  const metrics = [
    'Real-time performance dashboards',
    'Customer satisfaction scores (CSAT)',
    'First response time tracking',
    'Resolution time analytics',
    'Agent performance metrics',
    'Ticket volume trends',
    'Sentiment analysis reports',
    'Custom KPI tracking',
  ]

  const insights = [
    {
      title: 'Performance Metrics',
      description: 'Track response times, resolution rates, and agent productivity in real-time',
      icon: Activity,
    },
    {
      title: 'Customer Insights',
      description: 'Understand customer behavior, satisfaction trends, and pain points',
      icon: TrendingUp,
    },
    {
      title: 'Visual Reports',
      description: 'Beautiful charts and graphs that make data easy to understand',
      icon: PieChart,
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Home
        </Link>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto">
            <BarChart className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
            Comprehensive Analytics
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Make data-driven decisions with powerful analytics and insights. Track every metric
            that matters to your support team.
          </p>
        </div>
      </section>

      {/* Metrics Grid */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-12">
            <LineChart className="w-8 h-8 text-blue-600" />
            <h2 className="text-3xl font-bold text-center">Metrics You Can Track</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            {metrics.map((metric, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg"
              >
                <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">{metric}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Insights */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Actionable Insights</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {insights.map((insight, index) => {
              const Icon = insight.icon
              return (
                <div
                  key={index}
                  className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg"
                >
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{insight.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400">{insight.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Sample Dashboard Preview */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Dashboard Preview</h2>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
            <div className="grid grid-cols-4 gap-6 mb-8">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Tickets</div>
                <div className="text-3xl font-bold text-blue-600">1,247</div>
                <div className="text-xs text-green-600 mt-1">↑ 12% from last month</div>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Response</div>
                <div className="text-3xl font-bold text-purple-600">2.3m</div>
                <div className="text-xs text-green-600 mt-1">↓ 15% faster</div>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">CSAT Score</div>
                <div className="text-3xl font-bold text-green-600">94%</div>
                <div className="text-xs text-green-600 mt-1">↑ 3% improvement</div>
              </div>
              <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Active Chats</div>
                <div className="text-3xl font-bold text-orange-600">28</div>
                <div className="text-xs text-gray-500 mt-1">Real-time</div>
              </div>
            </div>
            <div className="h-64 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg flex items-center justify-center">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <BarChart className="w-16 h-16 mx-auto mb-2 opacity-50" />
                <p>Interactive charts and graphs</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">See Your Data Come to Life</h2>
          <p className="text-xl mb-8 text-blue-100">
            Start making data-driven decisions today
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition text-lg font-semibold"
          >
            Try Analytics Free
          </Link>
        </div>
      </section>
    </div>
  )
}
