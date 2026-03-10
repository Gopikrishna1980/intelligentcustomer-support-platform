'use client'

import { useEffect, useState } from 'react'
import { analyticsApi } from '@/lib/api'
import { TrendingUp, TrendingDown, Minus, Users, Clock } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { formatDuration } from '@/lib/utils'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function AnalyticsPage() {
  const [dashboard, setDashboard] = useState<any>(null)
  const [trends, setTrends] = useState([])
  const [categoryDistribution, setCategoryDistribution] = useState([])
  const [agentPerformance, setAgentPerformance] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    try {
      const [dashboardRes, trendsRes, categoryRes, agentRes] = await Promise.all([
        analyticsApi.getDashboard(),
        analyticsApi.getTicketTrends(30),
        analyticsApi.getTicketsByCategory(),
        analyticsApi.getAgentPerformance(),
      ])

      setDashboard(dashboardRes.data)
      setTrends(trendsRes.data)
      setCategoryDistribution(categoryRes.data)
      setAgentPerformance(agentRes.data)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      </div>
    )
  }

  const getTrendIcon = (trend: string) => {
    if (trend === 'improving') return <TrendingUp className="w-4 h-4 text-green-600" />
    if (trend === 'declining') return <TrendingDown className="w-4 h-4 text-red-600" />
    return <Minus className="w-4 h-4 text-gray-600" />
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
        Analytics Dashboard
      </h1>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Avg Response Time
            </h3>
            <Clock className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {dashboard?.avg_response_time_hours
              ? formatDuration(dashboard.avg_response_time_hours * 60)
              : 'N/A'}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Avg Resolution Time
            </h3>
            <Clock className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {dashboard?.avg_resolution_time_hours
              ? formatDuration(dashboard.avg_resolution_time_hours * 60)
              : 'N/A'}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Online Agents
            </h3>
            <Users className="w-5 h-5 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {dashboard?.online_agents || 0}
            <span className="text-lg text-gray-500 dark:text-gray-400">
              /{dashboard?.total_agents || 0}
            </span>
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Satisfaction
            </h3>
            <div className="flex items-center gap-1">
              {getTrendIcon(dashboard?.satisfaction_trend)}
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {dashboard?.avg_ticket_satisfaction
              ? (dashboard.avg_ticket_satisfaction * 20).toFixed(1)
              : 'N/A'}
            %
          </p>
        </div>
      </div>

      {/* Ticket Trends */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Ticket Trends (Last 30 Days)
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="created"
              stroke="#3b82f6"
              name="Created"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="resolved"
              stroke="#10b981"
              name="Resolved"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="open"
              stroke="#f59e0b"
              name="Open"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Category Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Tickets by Category
          </h2>
          {categoryDistribution.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={categoryDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry: any) => `${entry.category}: ${entry.percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {categoryDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2">
                {categoryDistribution.map((item: any, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      ></div>
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        {item.category || 'Uncategorized'}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {item.count} ({item.percentage}%)
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-12">
              No category data available
            </p>
          )}
        </div>

        {/* Agent Performance */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Agent Performance
          </h2>
          {agentPerformance.length > 0 ? (
            <div className="space-y-4">
              {agentPerformance.slice(0, 5).map((agent: any, index) => (
                <div key={index} className="border-b border-gray-200 dark:border-gray-700 last:border-0 pb-4 last:pb-0">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {agent.agent_name}
                      </h3>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {agent.current_workload} active tickets
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {agent.resolved_count} resolved
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        {agent.avg_satisfaction_score
                          ? (agent.avg_satisfaction_score * 20).toFixed(0)
                          : 'N/A'}
                        % satisfaction
                      </div>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(
                          (agent.current_workload / Math.max(...agentPerformance.map((a: any) => a.current_workload))) * 100,
                          100
                        )}%`,
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-12">
              No agent data available
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
