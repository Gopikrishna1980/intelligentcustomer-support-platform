'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { chatApi } from '@/lib/api'
import { connectChatWebSocket, disconnectChatWebSocket, ChatMessage } from '@/lib/socket'
import { Send, Bot, User as UserIcon, ArrowLeft, X } from 'lucide-react'
import { formatRelativeTime, getSentimentColor } from '@/lib/utils'

export default function ChatSessionPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params.id as string

  const [session, setSession] = useState<any>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [showEndDialog, setShowEndDialog] = useState(false)
  const [satisfaction, setSatisfaction] = useState(5)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const socketRef = useRef<any>(null)

  useEffect(() => {
    fetchSession()
    setupWebSocket()

    return () => {
      disconnectChatWebSocket()
    }
  }, [sessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchSession = async () => {
    try {
      const response = await chatApi.getSession(sessionId, true)
      setSession(response.data)
      setMessages(response.data.messages || [])
    } catch (error) {
      console.error('Failed to fetch session:', error)
    } finally {
      setLoading(false)
    }
  }

  const setupWebSocket = () => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const socket = connectChatWebSocket(sessionId, token)
    socketRef.current = socket

    socket.on('connect', () => {
      console.log('Connected to chat WebSocket')
    })

    socket.on('message', (data: ChatMessage) => {
      if (data.type === 'message' && data.message) {
        setMessages((prev) => [...prev, data.message])
        setIsTyping(false)
      } else if (data.type === 'typing') {
        setIsTyping(true)
        setTimeout(() => setIsTyping(false), 3000)
      } else if (data.type === 'agent_joined') {
        console.log('Agent joined the chat')
      }
    })

    socket.on('disconnect', () => {
      console.log('Disconnected from chat WebSocket')
    })
  }

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || sending) return

    setSending(true)
    try {
      await chatApi.sendMessage(sessionId, inputMessage, false)
      setInputMessage('')
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setSending(false)
    }
  }

  const handleEndSession = async () => {
    try {
      await chatApi.endSession(sessionId, satisfaction)
      router.push('/dashboard/chat')
    } catch (error) {
      console.error('Failed to end session:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading chat...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push('/dashboard/chat')}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="font-semibold text-gray-900 dark:text-white">
              Chat with {session?.is_bot_only ? 'AI Assistant' : 'Support Agent'}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {session?.is_active ? 'Active' : 'Ended'} • Started {formatRelativeTime(session?.created_at)}
            </p>
          </div>
        </div>
        {session?.is_active && (
          <button
            onClick={() => setShowEndDialog(true)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
          >
            End Session
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.map((message: any, index: number) => {
          const isBot = message.is_agent === false && message.sender_id !== session?.customer_id
          const isAgent = message.is_agent === true
          const isCustomer = !isBot && !isAgent

          return (
            <div
              key={message.id || index}
              className={`flex items-start gap-3 ${isCustomer ? 'flex-row-reverse' : ''}`}
            >
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  isBot
                    ? 'bg-blue-100 dark:bg-blue-900/30'
                    : isAgent
                    ? 'bg-green-100 dark:bg-green-900/30'
                    : 'bg-purple-100 dark:bg-purple-900/30'
                }`}
              >
                {isBot ? (
                  <Bot className="w-5 h-5 text-blue-600" />
                ) : (
                  <UserIcon className={`w-5 h-5 ${isAgent ? 'text-green-600' : 'text-purple-600'}`} />
                )}
              </div>
              <div className={`flex-1 ${isCustomer ? 'text-right' : ''}`}>
                <div
                  className={`inline-block max-w-[70%] p-3 rounded-lg ${
                    isCustomer
                      ? 'bg-blue-600 text-white'
                      : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
                <div className="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
                  <span>{formatRelativeTime(message.created_at)}</span>
                  {message.sentiment && (
                    <>
                      <span>•</span>
                      <span className={getSentimentColor(message.sentiment)}>
                        {message.sentiment}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>
          )
        })}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <Bot className="w-5 h-5 text-blue-600" />
            </div>
            <div className="bg-white dark:bg-gray-800 p-3 rounded-lg">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      {session?.is_active && (
        <form onSubmit={sendMessage} className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              disabled={sending}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || sending}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </div>
        </form>
      )}

      {/* End Session Dialog */}
      {showEndDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                End Chat Session
              </h3>
              <button
                onClick={() => setShowEndDialog(false)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              How satisfied were you with this chat session?
            </p>
            <div className="flex justify-between mb-6">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  onClick={() => setSatisfaction(rating)}
                  className={`w-12 h-12 rounded-full font-semibold transition ${
                    satisfaction === rating
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {rating}
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowEndDialog(false)}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleEndSession}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                End Session
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
