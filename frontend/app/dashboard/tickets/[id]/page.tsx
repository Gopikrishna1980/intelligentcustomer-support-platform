'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ticketsApi } from '@/lib/api'
import { ArrowLeft, Send, User as UserIcon, Bot } from 'lucide-react'
import { formatRelativeTime, getPriorityColor, getStatusColor, getSentimentColor } from '@/lib/utils'
import Link from 'next/link'

export default function TicketDetailPage() {
  const params = useParams()
  const ticketId = params.id as string
  
  const [ticket, setTicket] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [newMessage, setNewMessage] = useState('')
  const [sending, setSending] = useState(false)

  useEffect(() => {
    fetchTicket()
  }, [ticketId])

  const fetchTicket = async () => {
    try {
      const response = await ticketsApi.get(ticketId)
      setTicket(response.data)
    } catch (error) {
      console.error('Failed to fetch ticket:', error)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim() || sending) return

    setSending(true)
    try {
      await ticketsApi.addMessage(ticketId, newMessage, false)
      setNewMessage('')
      fetchTicket() // Refresh to show new message
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setSending(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading ticket...</p>
        </div>
      </div>
    )
  }

  if (!ticket) {
    return (
      <div className="text-center py-12">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Ticket not found
        </h3>
        <Link href="/dashboard/tickets" className="text-blue-600 hover:text-blue-700">
          Back to tickets
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/dashboard/tickets"
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-mono text-gray-500 dark:text-gray-400">
              {ticket.ticket_number}
            </span>
            <span
              className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(
                ticket.status
              )}`}
            >
              {ticket.status}
            </span>
            <span
              className={`text-xs px-2 py-1 rounded-full font-medium ${getPriorityColor(
                ticket.priority
              )}`}
            >
              {ticket.priority}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {ticket.title}
          </h1>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Description
            </h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {ticket.description}
            </p>
          </div>

          {/* Messages */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Messages ({ticket.messages?.length || 0})
            </h2>
            <div className="space-y-4 mb-6">
              {ticket.messages && ticket.messages.length > 0 ? (
                ticket.messages.map((message: any) => {
                  const isAgent = message.sender_id !== ticket.customer_id
                  return (
                    <div key={message.id} className="flex items-start gap-3">
                      <div
                        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                          isAgent
                            ? 'bg-green-100 dark:bg-green-900/30'
                            : 'bg-purple-100 dark:bg-purple-900/30'
                        }`}
                      >
                        <UserIcon
                          className={`w-5 h-5 ${
                            isAgent ? 'text-green-600' : 'text-purple-600'
                          }`}
                        />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {isAgent ? 'Support Agent' : 'You'}
                          </span>
                          {message.sentiment && (
                            <span
                              className={`text-xs ${getSentimentColor(
                                message.sentiment
                              )}`}
                            >
                              • {message.sentiment}
                            </span>
                          )}
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 mb-1">
                          {message.content}
                        </p>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatRelativeTime(message.created_at)}
                        </span>
                      </div>
                    </div>
                  )
                })
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No messages yet
                </p>
              )}
            </div>

            {/* New Message Form */}
            {ticket.status !== 'closed' && (
              <form onSubmit={sendMessage} className="border-t border-gray-200 dark:border-gray-700 pt-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    disabled={sending}
                  />
                  <button
                    type="submit"
                    disabled={!newMessage.trim() || sending}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
                  >
                    <Send className="w-5 h-5" />
                    Send
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Details */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
              Details
            </h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-gray-600 dark:text-gray-400">Category</dt>
                <dd className="text-sm font-medium text-gray-900 dark:text-white">
                  {ticket.category || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-600 dark:text-gray-400">Created</dt>
                <dd className="text-sm font-medium text-gray-900 dark:text-white">
                  {formatRelativeTime(ticket.created_at)}
                </dd>
              </div>
              {ticket.first_response_at && (
                <div>
                  <dt className="text-sm text-gray-600 dark:text-gray-400">First Response</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatRelativeTime(ticket.first_response_at)}
                  </dd>
                </div>
              )}
              {ticket.assigned_to && (
                <div>
                  <dt className="text-sm text-gray-600 dark:text-gray-400">Assigned To</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-white">
                    {ticket.agent?.full_name || 'N/A'}
                  </dd>
                </div>
              )}
              {ticket.ai_sentiment && (
                <div>
                  <dt className="text-sm text-gray-600 dark:text-gray-400">Sentiment</dt>
                  <dd className={`text-sm font-medium capitalize ${getSentimentColor(ticket.ai_sentiment)}`}>
                    {ticket.ai_sentiment}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}
