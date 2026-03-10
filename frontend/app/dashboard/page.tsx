'use client'

import { useEffect, useState } from 'react'
import { analyticsApi } from '@/lib/api'
import { BarChart3, MessageSquare, Ticket, Users, TrendingUp, Clock } from 'lucide-react'
import { formatDuration } from '@/lib/utils'

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await analyticsApi.getDashboard()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-gray-200 dark:bg-gray-800 rounded w-64"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  const cards = [
    {
      title: 'Total Tickets',
      value: stats?.total_tickets || 0,
      icon: Ticket,
      color: 'blue',
      subtitle: `${stats?.open_tickets || 0} open`,
    },
    {
      title: 'Active Chats',
      value: stats?.active_sessions || 0,
      icon: MessageSquare,
      color: 'green',
      subtitle: `${stats?.sessions_today || 0} today`,
    },
    {
      title: 'Online Agents',
      value: stats?.online_agents || 0,
      icon: Users,
      color: 'purple',
      subtitle: `${stats?.total_agents || 0} total`,
    },
    {
      title: 'Avg Response',
      value: stats?.avg_response_time_hours ? formatDuration(stats.avg_response_time_hours * 60) : 'N/A',
      icon: Clock,
      color: 'orange',
      subtitle: 'Response time',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <TrendingUp className="w-4 h-4" />
          <span>Last updated: just now</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => {
          const Icon = card.icon
          const colorClasses = {
            blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600',
            green: 'bg-green-100 dark:bg-green-900/30 text-green-600',
            purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600',
            orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600',
          }[card.color]

          return (
            <div
              key={card.title}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {card.title}
                  </p>
                  <p className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">
                    {card.value}
                  </p>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    {card.subtitle}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${colorClasses}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <a
          href="/dashboard/tickets/new"
          className="block bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 hover:shadow-md transition group"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg group-hover:scale-110 transition">
              <Ticket className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Create Ticket</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Open a new support request</p>
            </div>
          </div>
        </a>

        <a
          href="/dashboard/chat"
          className="block bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 hover:shadow-md transition group"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg group-hover:scale-110 transition">
              <MessageSquare className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Live Chat</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Chat with AI or agent</p>
            </div>
          </div>
        </a>

        <a
          href="/dashboard/analytics"
          className="block bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 hover:shadow-md transition group"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg group-hover:scale-110 transition">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Analytics</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">View insights and reports</p>
            </div>
          </div>
        </a>
      </div>

      {/* Satisfaction Score */}
      {stats && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Customer Satisfaction
          </h2>
          <div className="flex items-center gap-6">
            <div>
              <div className="text-4xl font-bold text-blue-600">
                {stats.avg_ticket_satisfaction ? (stats.avg_ticket_satisfaction * 20).toFixed(1) : 'N/A'}%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Average satisfaction
              </div>
            </div>
            <div className="flex-1">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{
                    width: `${stats.avg_ticket_satisfaction ? stats.avg_ticket_satisfaction * 20 : 0}%`,
                  }}
                ></div>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Trend: {stats.satisfaction_trend || 'stable'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
