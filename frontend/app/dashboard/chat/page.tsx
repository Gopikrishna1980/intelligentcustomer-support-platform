'use client'

import { useEffect, useState } from 'react'
import { chatApi } from '@/lib/api'
import { Plus, MessageSquare, Bot, User } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'
import Link from 'next/link'

export default function ChatListPage() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'active' | 'ended'>('all')

  useEffect(() => {
    fetchSessions()
  }, [filter])

  const fetchSessions = async () => {
    setLoading(true)
    try {
      const params: any = { page: 1, page_size: 20 }
      if (filter === 'active') params.is_active = true
      if (filter === 'ended') params.is_active = false

      const response = await chatApi.list(params)
      setSessions(response.data.items || [])
    } catch (error) {
      console.error('Failed to fetch sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = async () => {
    try {
      const response = await chatApi.startSession('Hello, I need help')
      window.location.href = `/dashboard/chat/${response.data.id}`
    } catch (error) {
      console.error('Failed to start chat:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Live Chat
        </h1>
        <button
          onClick={handleNewChat}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus className="w-5 h-5" />
          New Chat
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        {['all', 'active', 'ended'].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab as any)}
            className={`px-4 py-2 font-medium capitalize border-b-2 transition ${
              filter === tab
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Sessions List */}
      {loading ? (
        <div className="grid gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-gray-200 dark:bg-gray-800 rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
          <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No chat sessions yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Start a new chat to get help from our AI or agents
          </p>
          <button
            onClick={handleNewChat}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Start First Chat
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {sessions.map((session: any) => (
            <Link
              key={session.id}
              href={`/dashboard/chat/${session.id}`}
              className="block bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {session.is_bot_only ? (
                      <Bot className="w-5 h-5 text-blue-600" />
                    ) : (
                      <User className="w-5 h-5 text-green-600" />
                    )}
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      Session with {session.is_bot_only ? 'AI Bot' : 'Agent'}
                    </h3>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        session.is_active
                          ? 'bg-green-100 dark:bg-green-900/30 text-green-600'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                      }`}
                    >
                      {session.is_active ? 'Active' : 'Ended'}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span>{session.total_message_count || 0} messages</span>
                    <span>•</span>
                    <span>Started {formatRelativeTime(session.created_at)}</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
